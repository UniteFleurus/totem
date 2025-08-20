from typing import Optional

from ninja import FilterSchema, Field

#----------------------------------------------------
# User
#----------------------------------------------------

class UserFilterSchema(FilterSchema):
    username: Optional[str] = Field(None, q="username__icontains", title="Username", description="Search term in the username.")
    email: Optional[str] = Field(None, q="email__icontains", title="Email", description="Search term in the email.")
    is_active: Optional[bool] = Field(None, title="Is the user activated.", description="Search active or not users.")

    search: Optional[str] = Field(None, q=["username__icontains", "email__icontains"], title="Search Term", description="Search term in the username or in the email.")
