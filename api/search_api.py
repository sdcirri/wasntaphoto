from fastapi import APIRouter


search_router = APIRouter(prefix='/search', tags=['Search'])


# TODO: implement!
@search_router.post('/search')
async def search(

) -> list[int]:
    pass
