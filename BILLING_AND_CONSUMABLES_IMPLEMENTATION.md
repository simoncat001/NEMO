# Billing and Consumables Implementation Summary

## 1. Automatic Billing System

### Backend
- **Models**:
    - Updated `Tool` model in `backend/app/models/tool.py`:
        - Added `price_type` (0: Per Use, 1: Per Hour).
        - Added `price_per_use` (Numeric).
        - Added `price_per_hour` (Numeric).
    - Updated `UsageEvent` model in `backend/app/models/usage_event.py`:
        - Added `amount` (Numeric) to store the calculated cost.
- **Service**:
    - Updated `backend/app/services/usage_event_service.py`:
        - In `end_usage_event`, added logic to calculate `amount` based on the tool's pricing configuration and the usage duration.
- **Database**:
    - Created and executed `update_db_billing.py` to migrate the database schema.

### Frontend
- **Tool Management**:
    - Updated `ui/src/views/tools/ToolDetail.vue`:
        - Added form fields to configure pricing (Price Type, Price Per Use, Price Per Hour).
- **Usage History**:
    - Updated `ui/src/views/usage-events/UsageEventList.vue`:
        - Added "Cost" (费用) column to display the calculated amount.
    - Updated `ui/src/types/index.ts`:
        - Added `amount` to `UsageEvent` interface.

## 2. Consumables Management

### Backend
- **Models**:
    - Created `Consumable` model in `backend/app/models/consumable.py`.
    - Created `ConsumableWithdraw` model in `backend/app/models/consumable_withdraw.py`.
- **API**:
    - Implemented CRUD endpoints for Consumables.
    - Implemented Withdraw endpoint.

### Frontend
- **API Service**:
    - Created `ui/src/api/consumables.ts` for API communication.
- **Types**:
    - Added `Consumable` and `ConsumableWithdraw` interfaces to `ui/src/types/index.ts`.
- **Views**:
    - Created `ui/src/views/consumables/ConsumableList.vue`:
        - List view with search and filter.
        - Create/Edit dialog.
        - Delete functionality.
        - Withdraw dialog (领用).
- **Navigation**:
    - Added "Consumables" (耗材管理) route in `ui/src/router/index.ts`.
    - Added "Consumables" menu item in `ui/src/components/layout/Sidebar.vue`.

## Next Steps
- Verify the billing calculation logic with real usage scenarios.
- Test the consumables withdrawal flow.
- Consider adding a "Consumable Withdraw History" view if needed (currently only the withdrawal action is implemented).
