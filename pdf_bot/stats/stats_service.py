import platform
import shutil
import time
from datetime import datetime, timedelta, timezone
from typing import cast

import psutil
from sqlalchemy import func
from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from pdf_bot.database import DatabaseClient
from pdf_bot.database.models import UserModel


class StatsService:
    def __init__(self, db_client: DatabaseClient) -> None:
        self.db_client = db_client
        self._start_time = time.time()

    async def send_bot_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send bot statistics from the database."""
        msg = cast("Message", update.effective_message)

        with self.db_client.get_session() as session:
            total_users = session.query(func.count(UserModel.user_id)).scalar() or 0

            # Users by language (top 10)
            lang_stats = (
                session.query(UserModel.language, func.count(UserModel.user_id))
                .group_by(UserModel.language)
                .order_by(func.count(UserModel.user_id).desc())
                .limit(10)
                .all()
            )

            # Users registered today
            today_start = datetime.now(tz=timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            new_today = (
                session.query(func.count(UserModel.user_id))
                .filter(UserModel.created_at >= today_start)
                .scalar()
                or 0
            )

            # Users registered this week (last 7 days)
            week_ago = datetime.now(tz=timezone.utc) - timedelta(days=7)
            new_week = (
                session.query(func.count(UserModel.user_id))
                .filter(UserModel.created_at >= week_ago)
                .scalar()
                or 0
            )

            # Users registered this month (last 30 days)
            month_ago = datetime.now(tz=timezone.utc) - timedelta(days=30)
            new_month = (
                session.query(func.count(UserModel.user_id))
                .filter(UserModel.created_at >= month_ago)
                .scalar()
                or 0
            )

        # Bot uptime
        uptime_secs = int(time.time() - self._start_time)
        days, remainder = divmod(uptime_secs, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m"

        # Language stats formatted
        lang_lines = ""
        for lang, count in lang_stats:
            pct = (count / total_users * 100) if total_users > 0 else 0
            lang_lines += f"  <code>{lang:<8}</code> → {count} ({pct:.1f}%)\n"

        text = (
            "📊 <b>Estadísticas del Bot</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 <b>Usuarios totales:</b> {total_users:,}\n"
            f"🆕 <b>Nuevos hoy:</b> {new_today:,}\n"
            f"📅 <b>Últimos 7 días:</b> {new_week:,}\n"
            f"🗓 <b>Últimos 30 días:</b> {new_month:,}\n\n"
            f"⏱ <b>Uptime:</b> {uptime_str}\n\n"
            "🌍 <b>Top idiomas:</b>\n"
            f"{lang_lines}"
        )

        await msg.reply_text(text, parse_mode=ParseMode.HTML)

    async def send_vps_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send VPS/server statistics."""
        msg = cast("Message", update.effective_message)

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"

        # Memory
        mem = psutil.virtual_memory()
        mem_total_gb = mem.total / (1024**3)
        mem_used_gb = mem.used / (1024**3)
        mem_bar = _progress_bar(mem.percent)

        # Swap
        swap = psutil.swap_memory()
        swap_total_gb = swap.total / (1024**3)
        swap_used_gb = swap.used / (1024**3)

        # Disk
        disk = shutil.disk_usage("/")
        disk_total_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)
        disk_pct = (disk.used / disk.total) * 100
        disk_bar = _progress_bar(disk_pct)

        # System uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        sys_uptime = datetime.now(tz=timezone.utc) - boot_time
        sys_days = sys_uptime.days
        sys_hours, sys_rem = divmod(sys_uptime.seconds, 3600)
        sys_mins, _ = divmod(sys_rem, 60)

        # Network
        net = psutil.net_io_counters()
        net_sent_gb = net.bytes_sent / (1024**3)
        net_recv_gb = net.bytes_recv / (1024**3)

        # Load average (Unix only)
        try:
            load1, load5, load15 = psutil.getloadavg()
            load_str = f"{load1:.2f} / {load5:.2f} / {load15:.2f}"
        except (AttributeError, OSError):
            load_str = "N/A"

        text = (
            "🖥 <b>Estadísticas del VPS</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"💻 <b>Sistema:</b> {platform.system()} {platform.release()}\n"
            f"⏱ <b>Uptime:</b> {sys_days}d {sys_hours}h {sys_mins}m\n"
            f"📊 <b>Load avg:</b> {load_str}\n\n"
            f"🔧 <b>CPU:</b> {cpu_percent}% ({cpu_count} cores @ {cpu_freq_str})\n\n"
            f"🧠 <b>RAM:</b> {mem_used_gb:.1f} / {mem_total_gb:.1f} GB ({mem.percent}%)\n"
            f"  {mem_bar}\n\n"
            f"💾 <b>Swap:</b> {swap_used_gb:.1f} / {swap_total_gb:.1f} GB ({swap.percent}%)\n\n"
            f"📁 <b>Disco:</b> {disk_used_gb:.1f} / {disk_total_gb:.1f} GB ({disk_pct:.1f}%)\n"
            f"  {disk_bar}\n\n"
            f"🌐 <b>Red:</b>\n"
            f"  ↑ Enviado: {net_sent_gb:.2f} GB\n"
            f"  ↓ Recibido: {net_recv_gb:.2f} GB\n"
        )

        await msg.reply_text(text, parse_mode=ParseMode.HTML)


def _progress_bar(percent: float, length: int = 15) -> str:
    """Generate a text progress bar."""
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent:.1f}%"
