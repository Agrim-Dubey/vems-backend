from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Security personnel — can search vehicles at the gate."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["STAFF", "ADMIN"]
        )


class IsAdminUser(BasePermission):
    """Admins only — can approve/reject registrations."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )