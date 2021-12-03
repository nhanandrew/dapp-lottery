from brownie import (
    network,
    config,
    accounts,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)
from brownie.convert.datatypes import _address_compare

FORKED_LOCAL_ENVIRONMENT = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIORNMENTS = ["development", "ganache-local"]


DECIMALS = 8
INITIAL_VALUE = 400000000000


def get_account(index=None, id=None):
    # load account from index
    if index:
        return accounts[index]
    # load account from id
    if id:
        return accounts.load(id)
    # local blockchain
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIORNMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENT
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined, else will deploy a mock of that contract and return it.

    Args:
        contract_name(string)
    Returns:
        brownie.network.contract.ProjectContract: The most recently deployed version
        MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIORNMENTS:
        if len(contract_type) <= 0:  # if no mocks already, deploy
            deploy_mocks()
        contract = contract_type[-1]
    else:
        # address
        contract_address = config["networks"][network.show_active()][contract_name]
        # MockV3Aggregator.abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 10**17 or 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # can use interface so you dont need to compile down to the abi
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Link token sent!")
    return tx
