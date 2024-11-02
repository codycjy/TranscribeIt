import sqlite3
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from config import DATABASE_PATH
from api.schemas import TaskStatus, TranscriptionResponse
from utils.logger import logger # TODO: use logger


class DBManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            self._initialized = True
            self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youtube_url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                summary TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                created_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                summary_provider TEXT,
                summary_model TEXT
            )
        """)
        self.conn.commit()

    async def create_task(self, url: str) -> int:
        def _create():
            cursor = self.conn.execute(
                """
                INSERT INTO transcriptions 
                (youtube_url, status, created_at) 
                VALUES (?, ?, ?)
                """,
                (str(url), TaskStatus.PENDING, datetime.now())
            )
            self.conn.commit()
            return cursor.lastrowid

        return await asyncio.to_thread(_create)

    async def get_task(self, task_id: int) -> Optional[TranscriptionResponse]:
        def _get():
            cursor = self.conn.execute(
                "SELECT * FROM transcriptions WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_response(row)
            return None

        return await asyncio.to_thread(_get)

    async def get_all_tasks(self) -> Optional[TranscriptionResponse]:
        def _get():
            cursor = self.conn.execute(
                "SELECT * FROM transcriptions"
            )
            rows = cursor.fetchall()
            return [self._row_to_response(row) for row in rows]

        return await asyncio.to_thread(_get)

    async def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
        **kwargs: Dict[str, Any]
    ) -> bool:
        def _update():
            set_values = ["status = ?"]
            params = [status]

            for key, value in kwargs.items():
                set_values.append(f"{key} = ?")
                params.append(value)

            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                set_values.append("completed_at = ?")
                params.append(datetime.now())

            params.append(task_id)

            query = f"""
                UPDATE transcriptions 
                SET {', '.join(set_values)}
                WHERE id = ?
            """

            self.conn.execute(query, params)
            self.conn.commit()
            return True

        return await asyncio.to_thread(_update)

    async def delete_task(self, task_id: int) -> bool:
        def _delete():
            self.conn.execute(
                "DELETE FROM transcriptions WHERE id = ?",
                (task_id,)
            )
            self.conn.commit()
            return True

        return await asyncio.to_thread(_delete)

    def _row_to_response(self, row) -> TranscriptionResponse:
        return TranscriptionResponse(
            id=row[0],
            youtube_url=row[1],
            title=row[2],
            content=row[3],
            summary=row[4],
            status=TaskStatus(row[5]),
            error_message=row[6],
            created_at=row[7],
            completed_at=row[8]
        )

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
