import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

load_dotenv(override=True)

_mongo_client = None

def _get_db():
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri or "<username>" in uri:
            raise ValueError("MONGODB_URI is missing or invalid in .env")
        _mongo_client = AsyncIOMotorClient(uri)
    return _mongo_client["startup_ai"]

def authenticate_mcp_client(ctx: Context):
    if not ctx or not ctx.request_context or not hasattr(ctx.request_context, "request"):
        raise ValueError("Unauthorized: Missing request context")
    
    request = ctx.request_context.request
    auth_header = request.headers.get("Authorization")
    expected_key = os.getenv("MCP_API_KEY", "default-dev-key")
    
    if not auth_header or auth_header != f"Bearer {expected_key}":
        raise ValueError("Unauthorized: Invalid MCP API Key")

def register_tools(mcp: FastMCP):
    
    @mcp.tool()
    async def search_documents(query: str) -> str:
        from app.rag.vectorstore import get_vectorstore
        try:
            vs = get_vectorstore()
            docs = vs.similarity_search(query, k=2)
            if not docs:
                return "No relevant documents found."
            context = [f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs]
            return "\n\n---\n\n".join(context)
        except Exception as e:
            return f"Error searching documents: {str(e)}"

    @mcp.tool()
    async def get_database_schema() -> str:
        try:
            db = _get_db()
            collections = await db.list_collection_names()
            schema_info = {}
            for coll_name in collections:
                sample = await db[coll_name].find_one()
                if sample:
                    sample.pop('_id', None)
                schema_info[coll_name] = sample or "Empty Collection"
            return json.dumps(schema_info, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def execute_mongo_query(collection_name: str, filter_json: str, limit: int = 10) -> str:
        try:
            db = _get_db()
            try:
                query_filter = json.loads(filter_json)
            except json.JSONDecodeError:
                return "Error: Invalid JSON string."
            
            cursor = db[collection_name].find(query_filter).limit(min(limit, 50))
            results = []
            async for document in cursor:
                document.pop('_id', None)
                results.append(document)
            return json.dumps(results, indent=2, default=str) if results else "0 results."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_overdue_invoices(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            cursor = db.invoices.find({"status": "Overdue"}).limit(50)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            return json.dumps(results, indent=2, default=str) if results else "No overdue invoices."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_expense_report(ctx: Context, category: str = "") -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            query_filter = {}
            if category:
                query_filter["category"] = category

            cursor = db.expenses.find(query_filter).limit(50)
            expenses = []
            category_totals = {}
            async for doc in cursor:
                doc.pop('_id', None)
                expenses.append(doc)
                cat = doc.get("category", "Uncategorized")
                category_totals[cat] = category_totals.get(cat, 0) + doc.get("amount", 0)

            summary = {
                "total_expenses": sum(category_totals.values()),
                "by_category": category_totals,
                "details": expenses[:10]
            }
            return json.dumps(summary, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_revenue_summary(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            cursor = db.payments.find({}).limit(500)
            total, count = 0, 0
            by_type = {}
            async for doc in cursor:
                val = doc.get("payment_value", 0)
                total += val
                ptype = doc.get("payment_type", "unknown")
                by_type[ptype] = by_type.get(ptype, 0) + val
                count += 1

            return json.dumps({
                "total_revenue": total,
                "total_transactions": count,
                "by_type": by_type
            }, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_sales_pipeline(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            cursor = db.orders.find({}).limit(500)
            pipeline = {}
            async for doc in cursor:
                status = doc.get("order_status", "unknown")
                if status not in pipeline:
                    pipeline[status] = {"count": 0, "order_ids": []}
                pipeline[status]["count"] += 1
                if len(pipeline[status]["order_ids"]) < 3:
                    pipeline[status]["order_ids"].append(doc.get("order_id", ""))

            return json.dumps({"pipeline": pipeline}, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def search_customers(ctx: Context, city: str = "", state: str = "", limit: int = 10) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            query_filter = {}
            if city:
                query_filter["customer_city"] = {"$regex": city, "$options": "i"}
            if state:
                query_filter["customer_state"] = state.upper()

            cursor = db.customers.find(query_filter).limit(min(limit, 50))
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            return json.dumps(results, indent=2, default=str) if results else "No customers found."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def search_support_tickets(ctx: Context, min_score: int = 0, max_score: int = 5, keyword: str = "", limit: int = 10) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            query_filter = {
                "review_score": {"$gte": min_score, "$lte": max_score}
            }
            if keyword:
                query_filter["review_comment_message"] = {"$regex": keyword, "$options": "i"}

            cursor = db.reviews.find(query_filter).limit(min(limit, 50))
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            return json.dumps(results, indent=2, default=str) if results else "No tickets found."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_blocked_tasks(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            cursor = db.tasks.find({
                "$or": [{"status": "Blocked"}, {"priority": {"$in": ["P0", "P1"]}, "status": {"$ne": "Done"}}]
            }).limit(50)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            return json.dumps(results, indent=2, default=str) if results else "No blocked tasks."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_operational_metrics(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            cursor = db.tasks.find({}).limit(500)
            by_status, by_priority, total = {}, {}, 0
            async for doc in cursor:
                total += 1
                status = doc.get("status", "Unknown")
                priority = doc.get("priority", "Unknown")
                by_status[status] = by_status.get(status, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1

            return json.dumps({"total": total, "status": by_status, "priority": by_priority}, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def lookup_employee(ctx: Context, name: str = "", department: str = "") -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            query_filter = {}
            if name:
                query_filter["name"] = {"$regex": name, "$options": "i"}
            if department:
                query_filter["department"] = {"$regex": department, "$options": "i"}

            cursor = db.employees.find(query_filter).limit(20)
            results = []
            async for doc in cursor:
                doc.pop('_id', None)
                results.append(doc)
            return json.dumps(results, indent=2, default=str) if results else "No employees found."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def get_department_summary(ctx: Context) -> str:
        try:
            authenticate_mcp_client(ctx)
            db = _get_db()
            emp_cursor = db.employees.find({}).limit(200)
            departments, employee_ids = {}, {}
            async for doc in emp_cursor:
                dept = doc.get("department", "Unknown")
                if dept not in departments:
                    departments[dept] = {"headcount": 0, "total_salary": 0, "total_expenses": 0}
                departments[dept]["headcount"] += 1
                departments[dept]["total_salary"] += doc.get("salary", 0)
                employee_ids[doc.get("employee_id")] = dept

            exp_cursor = db.expenses.find({}).limit(500)
            async for doc in exp_cursor:
                emp_id = doc.get("employee_id")
                if emp_id in employee_ids:
                    departments[employee_ids[emp_id]]["total_expenses"] += doc.get("amount", 0)

            return json.dumps(departments, indent=2, default=str)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def trigger_high_stakes_action(
        ctx: Context,
        org_id: str,
        action_type: str,
        target_type: str,
        target_id: str,
        payload_json: str,
        requires_approval: bool = True
    ) -> str:
        """
        Triggers a business action (e.g. ISSUE_REFUND, UPDATE_CRM). 
        If requires_approval is True, the action will be paused for a human manager.
        """
        try:
            authenticate_mcp_client(ctx)
            
            # Since the tools are run in the MCP server context, we import the engine directly.
            from app.engines.action_engine import create_action
            
            try:
                payload = json.loads(payload_json)
            except json.JSONDecodeError:
                return "Error: payload_json must be a valid JSON string."
                
            action_id = await create_action(
                organization_id=org_id,
                created_by="AI_AGENT",
                action_type=action_type,
                target={"type": target_type, "id": target_id},
                payload=payload,
                requires_approval=requires_approval
            )
            
            if requires_approval:
                return f"Action {action_type} successfully staged. Action ID: {action_id}. Waiting for human approval."
            else:
                # In a full system we would execute immediately, but for demo we just return it.
                return f"Action {action_type} successfully created (auto-approved). Action ID: {action_id}."
                
        except Exception as e:
            return f"Error triggering action: {str(e)}"

