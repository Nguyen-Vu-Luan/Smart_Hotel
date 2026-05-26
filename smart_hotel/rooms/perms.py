from rest_framework import permissions

class IsReviewOwner(permissions.BasePermission):
    """
    Chỉ cho phép khách hàng (chủ sở hữu) mới có quyền chỉnh sửa hoặc xóa bài đánh giá của chính họ.
    """
    def has_object_permission(self, request, view, obj):
        # obj ở đây chính là một bản ghi (instance) của model Review
        # Kiểm tra xem người dùng đang gửi request có phải là người đã đặt cái booking đó không
        return obj.booking.customer == request.user