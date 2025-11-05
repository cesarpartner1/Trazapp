from django.db import models


class ActivityLog(models.Model):
	"""Registro centralizado de eventos relevantes mostrados en el tablero."""

	EVENT_CREATE = 'create'
	EVENT_UPDATE = 'update'
	EVENT_DELETE = 'delete'
	EVENT_CHOICES = [
		(EVENT_CREATE, 'Creación'),
		(EVENT_UPDATE, 'Actualización'),
		(EVENT_DELETE, 'Eliminación'),
	]

	category = models.CharField(max_length=50)
	title = models.CharField(max_length=200)
	meta = models.CharField(max_length=200, blank=True)
	event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default=EVENT_CREATE)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.created_at:%Y-%m-%d %H:%M} · {self.title}"
