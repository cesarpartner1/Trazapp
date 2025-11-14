from django.db import models


class Enumerator(models.Model):
	document_number = models.CharField(max_length=50, unique=True)
	full_name = models.CharField(max_length=200, blank=True)
	phone = models.CharField(max_length=25, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.full_name or self.document_number


class Survey(models.Model):
	producer = models.ForeignKey(
		"producers.Producer",
		on_delete=models.CASCADE,
		related_name="surveys",
	)
	plot = models.ForeignKey(
		"producers.Plot",
		on_delete=models.CASCADE,
		related_name="surveys",
	)
	enumerator = models.ForeignKey(
		Enumerator,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="surveys",
	)

	global_id = models.CharField(max_length=64, unique=True)
	census_date = models.DateTimeField()
	creation_date = models.DateTimeField(null=True, blank=True)
	edit_date = models.DateTimeField(null=True, blank=True)

	reported_area_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
	cocoa_area_ha = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
	buyer = models.CharField(max_length=200, blank=True)

	crops = models.CharField(max_length=200, blank=True)
	other_crop = models.CharField(max_length=200, blank=True)
	insai_registered = models.CharField(max_length=50, blank=True)
	has_rubber = models.CharField(max_length=50, blank=True)
	training_received = models.CharField(max_length=100, blank=True)
	varieties = models.CharField(max_length=200, blank=True)
	plant_origin = models.CharField(max_length=100, blank=True)
	other_origin = models.CharField(max_length=200, blank=True)
	cultural_practices = models.CharField(max_length=200, blank=True)
	other_practice = models.CharField(max_length=200, blank=True)
	fertilizers = models.CharField(max_length=200, blank=True)
	pesticides = models.CharField(max_length=200, blank=True)
	pest_issues = models.CharField(max_length=200, blank=True)

	harvest_volume = models.IntegerField(null=True, blank=True)
	cocoa_plants = models.IntegerField(null=True, blank=True)
	plant_spacing = models.CharField(max_length=100, blank=True)

	families_supported = models.IntegerField(null=True, blank=True)
	seniors = models.IntegerField(null=True, blank=True)
	adults = models.IntegerField(null=True, blank=True)
	teens = models.IntegerField(null=True, blank=True)
	children = models.IntegerField(null=True, blank=True)
	female_total = models.IntegerField(null=True, blank=True)
	male_total = models.IntegerField(null=True, blank=True)
	highest_education = models.CharField(max_length=100, blank=True)

	workers_total = models.IntegerField(null=True, blank=True)
	workers_men = models.IntegerField(null=True, blank=True)
	workers_women = models.IntegerField(null=True, blank=True)
	workers_teens = models.IntegerField(null=True, blank=True)
	workers_children = models.IntegerField(null=True, blank=True)

	health_condition = models.CharField(max_length=100, blank=True)
	other_disease = models.CharField(max_length=200, blank=True)
	observations = models.TextField(blank=True)
	risk_eudr = models.CharField(max_length=50, blank=True)

	raw_properties = models.JSONField(default=dict, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("-census_date",)

	def __str__(self) -> str:
		return f"Encuesta {self.global_id}"
