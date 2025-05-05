from app.models import ItemPublic


class ItemDetailDTO(ItemPublic):
    """
    Data Transfer Object (DTO) for item details.
    """
    owner_name: str | None = None
    owner_job: str | None = None