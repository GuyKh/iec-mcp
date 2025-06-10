from datetime import datetime
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

# Assuming iec-api is installed as a package
from iec_api.iec_client import IecClient
from iec_api.models.jwt import JWT
from iec_api.models.remote_reading import ReadingResolution

mcp = FastMCP(name="IEC API MCP Server", dependencies=["iec-api"])

# Global client instance (for simplicity, consider dependency injection for production)
iec_client: Optional[IecClient] = None


@mcp.tool(description="Initiate login with a user ID, awaiting OTP verification.")
async def login_with_id(user_id: str | int):
    global iec_client
    iec_client = IecClient(user_id=user_id)
    await iec_client.login_with_id()
    return {
        "message": "Login initiated. Please use 'verify_otp' with the code sent to your device."
    }


@mcp.tool(description="Verify the OTP code to complete the login process.")
async def verify_otp(otp_code: str):
    global iec_client
    if not iec_client:
        raise ValueError("Login not initiated. Please use 'login_with_id' first.")

    success = await iec_client.verify_otp(otp_code)
    if success:
        return {"message": "OTP verified successfully. You are now logged in."}
    else:
        raise ValueError("OTP verification failed.")


class JWTTokenType(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str
    id_token: Optional[str] = None


@mcp.tool(description="Load an existing JWT token to authenticate the client.")
async def load_jwt_token(user_id: str | int, token: JWTTokenType):
    global iec_client
    if not iec_client:
        # If client not initialized, create it with a dummy user_id, then load token
        # This assumes user_id is not strictly needed for token loading itself,
        # but IecClient requires it for instantiation.
        # A more robust solution might involve refactoring IecClient or asking for user_id here.
        iec_client = IecClient(
            user_id=str(user_id)
        )  # Dummy ID, will be overridden by token

    jwt_token = JWT(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type=token.token_type,
        expires_in=token.expires_in,
        scope=token.scope,
        id_token=token.id_token,
    )
    await iec_client.load_jwt_token(jwt_token)
    return {"message": "JWT token loaded successfully. Client authenticated."}


async def _get_iec_client() -> IecClient:
    global iec_client
    if not iec_client or not iec_client.logged_in:
        raise ValueError(
            "IEC client not initialized or not logged in. Please use 'login_with_id' or 'load_jwt_token' first."
        )
    return iec_client


@mcp.tool(description="Retrieve customer data from the IEC API.")
async def get_customer():
    client = await _get_iec_client()
    customer = await client.get_customer()
    if customer:
        return customer.to_dict()
    return {"message": "No customer data found."}


@mcp.tool(
    description="Retrieve a list of accounts for the logged-in user from the IEC API.",
)
async def get_accounts():
    client = await _get_iec_client()
    accounts = await client.get_accounts()
    if accounts:
        return [account.to_dict() for account in accounts]
    return {"message": "No accounts found."}


@mcp.tool(
    description="Retrieve the default contract for a given BP number from the IEC API."
)
async def get_default_contract(bp_number: Optional[str] = None):
    client = await _get_iec_client()
    contract = await client.get_default_contract(bp_number=bp_number)
    if contract:
        return contract.to_dict()
    return {"message": "No default contract found."}


@mcp.tool(
    description="Retrieve a list of contracts for a given BP number from the IEC API."
)
async def get_contracts(bp_number: Optional[str] = None):
    client = await _get_iec_client()
    contracts = await client.get_contracts(bp_number=bp_number)
    if contracts:
        return [contract.to_dict() for contract in contracts]
    return {"message": "No contracts found."}


@mcp.tool(description="Get contract check information from the IEC API.")
async def get_contract_check(contract_id: str):
    client = await _get_iec_client()
    contract_check = await client.get_contract_check(contract_id=contract_id)
    if contract_check:
        return contract_check.to_dict()
    return {"message": "No contract check found."}


@mcp.tool(description="Get the last meter reading from the IEC API.")
async def get_last_meter_reading(bp_number: str, contract_id: str):
    client = await _get_iec_client()
    meter_reading = await client.get_last_meter_reading(
        bp_number=bp_number, contract_id=contract_id
    )
    if meter_reading:
        return meter_reading.to_dict()
    return {"message": "No last meter reading found."}


@mcp.tool(
    description="Retrieves the electric bill for a specific meter from the IEC API."
)
async def get_electric_bill(
    bp_number: Optional[str] = None, contract_id: Optional[str] = None
):
    client = await _get_iec_client()
    electric_bill = await client.get_electric_bill(
        bp_number=bp_number, contract_id=contract_id
    )
    if electric_bill:
        return electric_bill.to_dict()
    return {"message": "No electric bill found."}


@mcp.tool(description="Get PDF of invoice from IEC API and save it to a file.")
async def save_invoice_pdf_to_file(
    file_path: str,
    invoice_number: str,
    bp_number: Optional[str] = None,
    contract_id: Optional[str] = None,
):
    client = await _get_iec_client()
    await client.save_invoice_pdf_to_file(
        file_path=file_path,
        invoice_number=invoice_number,
        bp_number=bp_number,
        contract_id=contract_id,
    )
    return {"message": f"Invoice PDF saved to {file_path}"}


@mcp.tool(description="Send consumption report to email from the IEC API.")
async def send_consumption_report_to_mail(
    email: str,
    contract_id: Optional[str] = None,
    device_id: Optional[str] = None,
    device_code: Optional[str] = None,
):
    client = await _get_iec_client()
    success = await client.send_consumption_report_to_mail(
        email=email,
        contract_id=contract_id,
        device_id=device_id,
        device_code=device_code,
    )
    if success:
        return {"message": "Consumption report sent to mail successfully."}
    return {"message": "Failed to send consumption report to mail."}


@mcp.tool(description="Get a list of devices for the user from the IEC API.")
async def get_devices(contract_id: Optional[str] = None):
    client = await _get_iec_client()
    devices = await client.get_devices(contract_id=contract_id)
    if devices:
        return [device.to_dict() for device in devices]
    return {"message": "No devices found."}


@mcp.tool(description="Get a device by its device ID from the IEC API.")
async def get_device_by_device_id(device_id: str, contract_id: Optional[str] = None):
    client = await _get_iec_client()
    device = await client.get_device_by_device_id(
        device_id=device_id, contract_id=contract_id
    )
    if device:
        return device.to_dict()
    return {"message": "No device found with the given device ID."}


@mcp.tool(description="Get device details by device ID from the IEC API.")
async def get_device_details_by_device_id(device_id: str):
    client = await _get_iec_client()
    device_details = await client.get_device_details_by_device_id(device_id=device_id)
    if device_details:
        return [detail.to_dict() for detail in device_details]
    return {"message": "No device details found for the given device ID."}


@mcp.tool(description="Get device details by device ID and code from the IEC API.")
async def get_device_details_by_device_id_and_code(device_id: str, device_code: str):
    client = await _get_iec_client()
    device_details = await client.get_device_details_by_device_id_and_code(
        device_id=device_id, device_code=device_code
    )
    if device_details:
        return device_details.to_dict()
    return {"message": "No device details found for the given device ID and code."}


@mcp.tool(
    description="Retrieves a remote reading for a specific meter from the IEC API."
)
async def get_remote_reading(
    meter_serial_number: str,
    meter_code: int,
    last_invoice_date: datetime,
    from_date: datetime,
    resolution: ReadingResolution = ReadingResolution.DAILY,
    contract_id: Optional[str] = None,
):
    client = await _get_iec_client()
    remote_reading = await client.get_remote_reading(
        meter_serial_number=meter_serial_number,
        meter_code=meter_code,
        last_invoice_date=last_invoice_date,
        from_date=from_date,
        resolution=resolution,
        contract_id=contract_id,
    )
    if remote_reading:
        return remote_reading.to_dict()
    return {"message": "No remote reading found."}


@mcp.tool(description="Get the device type for a contract from the IEC API.")
async def get_device_type(
    bp_number: Optional[str] = None, contract_id: Optional[str] = None
):
    client = await _get_iec_client()
    device_type = await client.get_device_type(
        bp_number=bp_number, contract_id=contract_id
    )
    if device_type:
        return device_type.to_dict()
    return {"message": "No device type found."}


@mcp.tool(description="Get billing invoices for a contract from the IEC API.")
async def get_billing_invoices(
    bp_number: Optional[str] = None, contract_id: Optional[str] = None
):
    client = await _get_iec_client()
    billing_invoices = await client.get_billing_invoices(
        bp_number=bp_number, contract_id=contract_id
    )
    if billing_invoices:
        return billing_invoices.to_dict()
    return {"message": "No billing invoices found."}


@mcp.tool("get_kwh_tariff", "Get kWh tariff from the IEC API.")
async def get_kwh_tariff():
    client = await _get_iec_client()
    tariff = await client.get_kwh_tariff()
    return {"kwh_tariff": tariff}


@mcp.tool(description="Get distribution tariff from the IEC API.")
async def get_distribution_tariff(phase_count: Optional[int] = None):
    client = await _get_iec_client()
    tariff = await client.get_distribution_tariff(phase_count=phase_count)
    return {"distribution_tariff": tariff}


@mcp.tool(description="Get delivery tariff from the IEC API.")
async def get_delivery_tariff(phase_count: Optional[int] = None):
    client = await _get_iec_client()
    tariff = await client.get_delivery_tariff(phase_count=phase_count)
    return {"delivery_tariff": tariff}


@mcp.tool("get_kva_tariff", "Get KVA tariff from the IEC API.")
async def get_kva_tariff():
    client = await _get_iec_client()
    tariff = await client.get_kva_tariff()
    return {"kva_tariff": tariff}


@mcp.tool(description="Get power size from the IEC API.")
async def get_power_size(connection: Optional[str] = None):
    client = await _get_iec_client()
    power_size = await client.get_power_size(connection=connection)
    return {"power_size": power_size}


@mcp.tool("get_usage_calculator", "Get Usage Calculator module from the IEC API.")
async def get_usage_calculator():
    client = await _get_iec_client()
    calculator = await client.get_usage_calculator()
    # The UsageCalculator object itself might be complex, returning a simple message for now.
    # If specific methods of the calculator are needed, they should be exposed as separate tools.
    return {"message": "Usage Calculator module retrieved successfully."}


@mcp.tool(description="Get equipment for the account from the Masa API.")
async def get_masa_equipment_by_account(account_id: Optional[str] = None):
    client = await _get_iec_client()
    equipment = await client.get_masa_equipment_by_account(account_id=account_id)
    if equipment:
        return equipment.to_dict()
    return {"message": "No Masa equipment found for the given account."}


@mcp.tool(description="Get Masa User Profile from the Masa API.")
async def get_masa_user_profile():
    client = await _get_iec_client()
    user_profile = await client.get_masa_user_profile()
    if user_profile:
        return user_profile.to_dict()
    return {"message": "No Masa user profile found."}


@mcp.tool(description="Get Masa Cities from the Masa API.")
async def get_masa_cities():
    client = await _get_iec_client()
    cities = await client.get_masa_cities()
    if cities:
        return [city.to_dict() for city in cities]
    return {"message": "No Masa cities found."}


@mcp.tool(description="Get Masa Order Categories from the Masa API.")
async def get_masa_order_categories():
    client = await _get_iec_client()
    order_categories = await client.get_masa_order_categories()
    if order_categories:
        return [category.to_dict() for category in order_categories]
    return {"message": "No Masa order categories found."}


@mcp.tool(description="Get Masa Volt Levels from the Masa API.")
async def get_masa_volt_levels():
    client = await _get_iec_client()
    volt_levels = await client.get_masa_volt_levels()
    if volt_levels:
        return [level.to_dict() for level in volt_levels]
    return {"message": "No Masa volt levels found."}


@mcp.tool(description="Get Masa Order Titles from the Masa API.")
async def get_masa_order_titles(account_id: Optional[str] = None):
    client = await _get_iec_client()
    titles = await client.get_masa_order_titles(account_id=account_id)
    if titles:
        return titles.to_dict()
    return {"message": "No Masa order titles found."}


@mcp.tool("Get Masa Lookup data from the Masa API.")
async def get_masa_lookup():
    client = await _get_iec_client()
    lookup = await client.get_masa_lookup()
    if lookup:
        return lookup.to_dict()
    return {"message": "No Masa lookup data found."}


@mcp.tool(description="Get Masa connection size from Masa API based on account.")
async def get_masa_connection_size_from_masa(account_id: Optional[str] = None):
    client = await _get_iec_client()
    connection_size = await client.get_masa_connection_size_from_masa(
        account_id=account_id
    )
    if connection_size:
        return {"connection_size": connection_size}
    return {"message": "No Masa connection size found."}


@mcp.tool(
    description="Get User Profile for the Account from Fault Portal.",
)
async def get_fault_portal_user_profile():
    client = await _get_iec_client()
    user_profile = await client.get_fault_portal_user_profile()
    if user_profile:
        return user_profile.to_dict()
    return {"message": "No Fault Portal user profile found."}


@mcp.tool(description="Get Outages for the Account from Fault Portal.")
async def get_fault_portal_outages_by_account(account_id: Optional[str] = None):
    client = await _get_iec_client()
    outages = await client.get_fault_portal_outages_by_account(account_id=account_id)
    if outages:
        return [outage.to_dict() for outage in outages]
    return {"message": "No Fault Portal outages found for the given account."}


if __name__ == "__main__":
    mcp.run()
