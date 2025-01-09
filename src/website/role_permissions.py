from user.access_rights import register_permission


register_permission('totem.websitepage.create', "Create Website Page", is_public=False)
register_permission('totem.websitepage.read', "Read Website Page", is_public=False)
register_permission('totem.websitepage.update', "Update Website Page", is_public=False)
register_permission('totem.websitepage.delete', "Delete Website Page", is_public=False)

register_permission('totem.websitemenu.create',
                    "Create Website Menu", is_public=False)
register_permission('totem.websitemenu.read',
                    "Read Website Menu", is_public=False)
register_permission('totem.websitemenu.update',
                    "Update Website Menu", is_public=False)
register_permission('totem.websitemenu.delete',
                    "Delete Website Menu", is_public=False)
