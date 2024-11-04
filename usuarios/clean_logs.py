from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import csv
import os
from .models import *
from django.db import transaction

class LogManager:
    def __init__(self, retention_days=30, batch_size=1000, archive_dir='log_archives'):
        self.retention_days = retention_days
        self.batch_size = batch_size
        self.archive_dir = archive_dir
        
        # Crear directorio de archivos si no existe
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)

    def clean_old_logs(self):
        """Elimina logs más antiguos que retention_days"""
        cutoff_date = timezone.now() - timedelta(days=self.retention_days)
        
        # Obtener cantidad de logs a eliminar
        logs_to_delete = UserActivityLog.objects.filter(
            timestamp__lt=cutoff_date
        )
        
        # Si hay logs para eliminar, archivarlos primero
        if logs_to_delete.exists():
            self.archive_logs(logs_to_delete)
            
            # Eliminar en lotes para no sobrecargar la memoria
            total_deleted = 0
            while True:
                # Usar slice para procesar en lotes
                batch_ids = logs_to_delete[:self.batch_size].values_list('id', flat=True)
                if not batch_ids:
                    break
                    
                # Eliminar el lote actual
                deleted_count = UserActivityLog.objects.filter(id__in=batch_ids).delete()[0]
                total_deleted += deleted_count
                
                if deleted_count < self.batch_size:
                    break
                    
            return total_deleted
        return 0

    def archive_logs(self, queryset):
        """Archiva logs en un archivo CSV"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs_archive_{timestamp}.csv'
        filepath = os.path.join(self.archive_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Escribir encabezados
            writer.writerow(['usuario', 'acción', 'objetivo', 'aplicación', 'fecha_hora'])
            
            # Escribir logs en lotes
            for log in queryset.iterator(chunk_size=self.batch_size):
                writer.writerow([
                    log.user.username,
                    log.action,
                    log.target,
                    log.app_name,
                    log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])

class Command(BaseCommand):
    help = 'Limpia logs antiguos y los archiva'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=15,
            help='Número de días de retención de logs'
        )

    def handle(self, *args, **options):
        log_manager = LogManager(retention_days=options['days'])
        deleted_count = log_manager.clean_old_logs()
        
        self.stdout.write(
            self.style.SUCCESS(f'Se eliminaron {deleted_count} logs antiguos')
        )

# Función auxiliar para usar en vistas
def get_filtered_logs(days=None, user=None, action=None):
    """
    Obtiene logs filtrados por diferentes criterios
    """
    queryset = UserActivityLog.objects.select_related('user')
    
    if days:
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=cutoff_date)
    
    if user:
        queryset = queryset.filter(user=user)
        
    if action:
        queryset = queryset.filter(action=action)
        
    return queryset.order_by('-timestamp')