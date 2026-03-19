from nutrack.categories.exceptions import CategoryNameConflictError, CategoryNotFoundError
from nutrack.categories.models import Category
from nutrack.categories.repository import CategoryRepository
from nutrack.categories.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)


def _build_response(category: Category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    async def list_categories(self, user_id: int) -> list[CategoryResponse]:
        categories = await self.repo.get_all_by_user(user_id)
        return [_build_response(c) for c in categories]

    async def create_category(
        self, user_id: int, data: CreateCategoryRequest
    ) -> CategoryResponse:
        existing = await self.repo.get_by_name_and_user(data.name, user_id)
        if existing:
            raise CategoryNameConflictError()
        category = await self.repo.create(
            user_id=user_id,
            name=data.name,
            color=data.color,
        )
        return _build_response(category)

    async def update_category(
        self, user_id: int, category_id: int, data: UpdateCategoryRequest
    ) -> CategoryResponse:
        category = await self.repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise CategoryNotFoundError()
        if data.name is not None and data.name != category.name:
            conflict = await self.repo.get_by_name_and_user(data.name, user_id)
            if conflict:
                raise CategoryNameConflictError()
        updates = {field: getattr(data, field) for field in data.model_fields_set}
        if updates:
            await self.repo.update(category, **updates)
        return _build_response(category)

    async def delete_category(self, user_id: int, category_id: int) -> None:
        deleted = await self.repo.delete_by_id_and_user(category_id, user_id)
        if not deleted:
            raise CategoryNotFoundError()
