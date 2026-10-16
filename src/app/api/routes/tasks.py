from fastapi import APIRouter, HTTPException, status

from src.app.schemas.voice import Task, TaskCreate, TaskReplace, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

tasks: list[dict[str, int | str | bool]] = []
next_task_id = 1


@router.get("", response_model=list[Task])
def get_tasks() -> list[Task]:
    return [Task.model_validate(task) for task in tasks]
    


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    global next_task_id

    task = Task(
        id=next_task_id,
        title=payload.title,
        done=payload.done,
    )
    tasks.append(task.model_dump())
    next_task_id += 1
    return task


@router.put("/{task_id}", response_model=Task)
def replace_task(
    task_id: int,
    payload: TaskReplace,
) -> Task:
    for index, task_data in enumerate(tasks):
        if task_data["id"] == task_id:
            replaced_task = Task(
                id=task_data["id"],
                title=payload.title,
                done=payload.done,
            )
            tasks[index] = replaced_task.model_dump()
            return replaced_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )



@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    payload: TaskUpdate,
) -> Task:
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)

    for index, task_data in enumerate(tasks):
        task = Task.model_validate(task_data)
        if task.id == task_id:
            updated_task = task.model_copy(update=updates)
            tasks[index] = updated_task.model_dump()
            return updated_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            del tasks[index]
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )
