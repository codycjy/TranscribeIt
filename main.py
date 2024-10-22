import streamlit as st
import whisper
import yt_dlp
import os
import sqlite3
import threading
from datetime import datetime
from config import (
    DOWNLOAD_DIR,
    WHISPER_MODEL,
    YTDL_OPTIONS,
    DATABASE_PATH,
    CREATE_TABLE_SQL,
    TaskStatus
)


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()


def create_task(url):
    """创建新任务"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.execute(
        "INSERT INTO transcriptions (youtube_url, status, created_at) VALUES (?, ?, ?)",
        (url, TaskStatus.PENDING, datetime.now())
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def update_task_status(task_id, status, title=None, content=None, error_message=None):
    """更新任务状态"""
    conn = sqlite3.connect(DATABASE_PATH)
    update_fields = ["status = ?"]
    params = [status]

    if title is not None:
        update_fields.append("title = ?")
        params.append(title)
    if content is not None:
        update_fields.append("content = ?")
        params.append(content)
    if error_message is not None:
        update_fields.append("error_message = ?")
        params.append(error_message)
    if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        update_fields.append("completed_at = ?")
        params.append(datetime.now())

    params.append(task_id)

    query = f"UPDATE transcriptions SET {', '.join(update_fields)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    conn.close()


def get_task_status(task_id):
    """获取任务状态"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.execute(
        "SELECT status, title, content, error_message FROM transcriptions WHERE id = ?",
        (task_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_transcriptions():
    """获取所有转写记录"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.execute(
        """SELECT id, youtube_url, title, content, status, error_message, 
           created_at, completed_at 
           FROM transcriptions ORDER BY created_at DESC"""
    )
    transcriptions = cursor.fetchall()
    conn.close()
    return transcriptions


def delete_transcription(transcription_id):
    """删除转写记录"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("DELETE FROM transcriptions WHERE id = ?",
                 (transcription_id,))
    conn.commit()
    conn.close()


def process_video(task_id, url):
    """处理视频的后台任务"""
    try:
        # 更新状态为下载中
        update_task_status(task_id, TaskStatus.DOWNLOADING)

        # 下载视频
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            audio_path = str(DOWNLOAD_DIR / f"{title}.mp3")

        # 更新标题
        update_task_status(task_id, TaskStatus.TRANSCRIBING, title=title)

        # 转写音频
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(audio_path)

        # 更新转写结果
        update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            content=result["text"]
        )

        # 清理音频文件
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"清理文件失败: {str(e)}")

    except Exception as e:
        # 处理错误
        update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))


def main():
    st.title("YouTube 视频转写器")

    # 创建两个标签页
    tab1, tab2 = st.tabs(["新建转写", "历史记录"])

    with tab1:
        # 输入YouTube URL
        url = st.text_input("输入YouTube视频URL", value="")

        if st.button("开始处理"):
            if url:
                # 创建任务并启动后台处理
                task_id = create_task(url)
                thread = threading.Thread(
                    target=process_video,
                    args=(task_id, url)
                )
                thread.daemon = True
                thread.start()

                st.success("任务已提交，请在历史记录中查看进度")
            else:
                st.warning("请输入有效的YouTube URL")

    with tab2:
        # 添加刷新按钮
        if st.button("刷新"):
            st.rerun()

        # 显示历史记录
        transcriptions = get_all_transcriptions()
        if transcriptions:
            for id, url, title, content, status, error_message, created_at, completed_at in transcriptions:
                # 构建标题显示
                display_title = f"{title if title else '处理中...'}"
                status_emoji = {
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.DOWNLOADING: "📥",
                    TaskStatus.TRANSCRIBING: "🔄",
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.FAILED: "❌"
                }.get(status, "")

                with st.expander(f"{status_emoji} {display_title} - {created_at}"):
                    st.markdown(f"**URL:** {url}")
                    st.markdown(f"**状态:** {status}")

                    if error_message:
                        st.error(f"错误信息: {error_message}")

                    if content:
                        st.text_area("转写内容", value=content,
                                     height=200, key=f"content_{id}")

                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button("删除", key=f"delete_{id}"):
                                delete_transcription(id)
                                st.rerun()
                        with col2:
                            st.download_button(
                                label="下载转写文本",
                                data=content,
                                file_name=f"{title}.txt",
                                mime="text/plain",
                                key=f"download_{id}"
                            )
                    elif status != TaskStatus.FAILED:
                        st.info("处理中...")
        else:
            st.info("暂无历史记录")

    # 显示配置信息
    st.sidebar.markdown("### 配置信息")
    st.sidebar.text(f"下载目录: {DOWNLOAD_DIR}")
    st.sidebar.text(f"Whisper模型: {WHISPER_MODEL}")
    st.sidebar.text(f"数据库: {DATABASE_PATH}")


if __name__ == "__main__":
    init_db()
    main()
