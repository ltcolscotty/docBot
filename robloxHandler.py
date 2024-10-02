from roblox import Client


async def get_role_count(group_id):
    """
    Gets number of people in each role

    Args:
        group_id: int

    Returns:
        Dictionary: {role name: count}
    """
    client = Client()
    group = await client.get_group(group_id)
    roles = await group.get_roles()
    return_dict = {}
    for role in roles:
        return_dict[role.name] = role.member_count
    return return_dict
