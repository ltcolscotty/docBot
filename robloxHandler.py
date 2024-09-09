import asyncio
from roblox import Client

import doc_config


async def get_role_count(group_id):
    client = Client()
    group = await client.get_group(group_id)
    roles = await group.get_roles()
    for role in roles:
        print(f"Role: {role.name}, Member Count: {role.member_count}")


asyncio.run(get_role_count(doc_config.mod_group))