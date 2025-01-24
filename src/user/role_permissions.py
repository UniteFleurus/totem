from user.access_rights import register_permission


register_permission('totem.user.create', "Create User", is_public=False)
register_permission('totem.user.read', "Read User", is_public=False)
register_permission('totem.user.update', "Update User", is_public=False)
register_permission('totem.user.delete', "Delete User", is_public=False)
