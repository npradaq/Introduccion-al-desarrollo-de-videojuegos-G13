import esper

from src.ecs.components.c_attach_to import CAttachTo
from src.ecs.components.c_transform import CTransform


def system_attach_to(world: esper.World) -> None:
    components = world.get_components(CTransform, CAttachTo)
    for entity, (c_transform, c_attach) in components:
        if not world.entity_exists(c_attach.parent_id):
            world.delete_entity(entity)
            continue
        parent_t = world.component_for_entity(c_attach.parent_id, CTransform)
        c_transform.position.x = parent_t.position.x + c_attach.offset.x
        c_transform.position.y = parent_t.position.y + c_attach.offset.y
