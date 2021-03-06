# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import utils

# Constants
# Transaction type values
TYPE_CHOICES = (
    (1, _('In')),
    (2, _('Used')),
    (4, _('Perished')),
    (8, _('Physical Count')),
    (9, _('Other')),
)

# Medicine "dangerosity" list values
DRUG_LIST_CHOICES = (
    (0, _('None')),
    (1, _('List I')),
    (2, _('List II')),
    (9, _('Narcotics')),
)

# Dosage form possible values
DRUG_FORM_CHOICES = (
    (1, _('Tablet')),
    (2, _('Ampoule')),
    (3, _('Capsule')),
    (5, 'Lyophilisat oral'),
    (6, 'Sachet'),
    (7, _('Suppository')),
    (8, 'Capsule'),

    (10, 'Tube pommade'),
    (11, 'Tube crème'),
    (12, 'Gel buccal'),
    (13, 'Unidose gel'),

    (40, 'Seringue pré-remplie'),

    (50, 'Solution pour perfusion'),
    (51, 'Solution injectable'),
    (52, 'Solution acqueuse'),
    (53, 'Solution moussante'),
    (54, 'Solution alcoolisée'),
    (55, 'Solution auriculaire'),
    (56, 'Solution'),

    (90, 'Bouteille'),
    (91, 'Flacon'),
    (92, 'Dispositif'),
    (93, 'Pansement adhésif cutané'),
    (94, 'Unidose'),

    (100, 'Collyre unidose'),
    (101, 'Collyre flacon'),
    (102, 'Collutoire'),
    (103, 'Pommade ophtalmique'),
)

# Route of administration possible values
DRUG_ROA_CHOICES = (
    (1, _('Oral')),

    (5, _('Parenteral')),
    (6, _('Subcutaneous')),

    (10, _('Topical')),
    (11, _('Transdermal')),

    (20, _('Inhalation')),
    (21, _('Nebulization')),

    (30, _('Buccal')),
    (31, _('Sublingual')),
    (32, _('Mouthwash')),

    (40, _('Rectal')),
    (41, _('Vaginal')),

    (50, _('Ocular')),
)


# Models
class Allowance(models.Model):
    """Model for articles and medicines allowances."""
    name = models.CharField(max_length=100)  # Example: Dotation A
    author = models.CharField(max_length=100)  # Example: CCMM Purpan
    signature = models.CharField(max_length=200)
    date = models.DateField()
    version = models.CharField(max_length=20)
    # For use with complements.
    # True will add quantity, false will be treated as an absolute quantity.
    additional = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', )


class GroupManager(models.Manager):
    """Manager for class MedicineGroup and MaterialGroup.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)


class MoleculeGroup(models.Model):
    """Model for groups attached to a :model:`inventory.Molecule` instance."""
    objects = GroupManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Cardiology
    order = models.IntegerField()  # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, _(self.name))

    def natural_key(self):
            return (self.name,)

    class Meta:
        ordering = ("order", "name",)
        unique_together = ('name', )


class EquipmentGroup(models.Model):
    """Model for groups attached to a :model:`inventory.Equipment` instance."""
    objects = GroupManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Reanimation
    order = models.IntegerField()  # Example: 1

    def __unicode__(self):
        return u"{0}. {1}".format(self.order, _(self.name))

    def natural_key(self):
            return (self.name,)

    class Meta:
        ordering = ("order", "name",)
        unique_together = ('name', )


class TagManager(models.Manager):
    """
    Manager for class Tag.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Tag(models.Model):
    """Stores tags attached to a :model:`inventory.Equipment` or
    model:`inventory.Molecule` instance.
    """
    objects = TagManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Common Use
    comment = models.TextField(blank=True, null=True)  # Description of the tag

    def __unicode__(self):
        return unicode(_(self.name))

    def natural_key(self):
            return (self.name,)

    class Meta:
        ordering = ("name",)
        unique_together = ('name',)


class Location(models.Model):
    """Stores locations attached to a :model:`inventory.Equipment` or
    model:`inventory.Molecule` instance.
    """
    primary = models.CharField(_("Primary"), max_length=100)  # Ex: Pharmacie
    secondary = models.CharField(_("Secondary"), max_length=100, blank=True, null=True)  # Example: Tiroir 2

    def __unicode__(self):
        if self.secondary:
            return u"{0} > {1}".format(_(self.primary), _(self.secondary))
        else:
            return unicode(_(self.primary))

    class Meta:
        ordering = ("primary", "secondary")


class QtyTransaction(models.Model):
    """
    Stores a quantity transaction related to :model:`inventory.Article`
    or :model:`inventory.Medicine`.

    There are 5 types of transactions:
    * 1 IN: a material is added,
    * 2 USED: the material is used for a treatment,
    * 4 PERISHED: the material has expired,
    * 8 PHYSICAL_COUNT: the stock is refreshed after a human count,
    * 9 OTHER: other reason.
    """

    transaction_type = models.PositiveIntegerField(_("Type"), choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)
    value = models.IntegerField(_("Value"), )

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"{0} ({1}: {2})".format(self.content_object, self.get_transaction_type_display(), self.value)


class Remark(models.Model):
    """Stores remarks attached to a :model:`inventory.Equipment` or
    :model:`inventory.Molecule` instance.
    """
    text = models.TextField(_("Text"), blank=True, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class MoleculeManager(models.Manager):
    """Manager for :model:`inventory.Molecule`."""
    def get_by_natural_key(self, name, roa, dosage_form, composition):
        return self.get(name=name, roa=roa, dosage_form=dosage_form, composition=composition)

    def missing(self):
        """Returns the quantity to order to meet the requirement."""
        inventory_settings = Settings.objects.latest('id')
        exp_delay = utils.delay(inventory_settings.expire_date_warning_delay)
        # Selection of available ReqQty
        allowance_list = inventory_settings.allowance.all()
        req_qty_list = MoleculeReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance').order_by('base')
        # Molecule list
        molecule_list = Molecule.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('medicine_set').order_by('name')
        # Medicine quantity transaction list
        qty_transaction_list = QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(Medicine))

        result_list = []
        # Selection of the current quantities
        for molecule in molecule_list:
            current_qty = 0
            for medicine in molecule.medicine_set.all():
                # Do not add quantity if any non-conformity of medicine (near) expired.
                if medicine.nc_molecule or medicine.nc_composition or medicine.exp_date <= exp_delay:
                    continue
                # Add quantity for other ones
                for transaction in qty_transaction_list:
                    if transaction.object_id == medicine.id:
                        current_qty += transaction.value

            # Then, parse required quantities
            required_qty = utils.req_qty_element(molecule, req_qty_list)

            # Finally, add the molecule with new attribute if current < required
            if current_qty < required_qty:
                molecule.missing = (required_qty - current_qty)
                result_list.append(molecule)

        return result_list


class Molecule(models.Model):
    """Stores molecule objects used as referent in an :model:`inventory.Allowance`."""
    objects = MoleculeManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Paracétamol
    roa = models.PositiveIntegerField(choices=DRUG_ROA_CHOICES)  # Example: dermal -- ROA: Route of Administration
    dosage_form = models.IntegerField(choices=DRUG_FORM_CHOICES)  # Example: "pill"
    composition = models.CharField(max_length=100)  # Example: 1000 mg
    medicine_list = models.PositiveIntegerField(choices=DRUG_LIST_CHOICES)  # Example: List I
    group = models.ForeignKey(MoleculeGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    allowances = models.ManyToManyField(Allowance, through='MoleculeReqQty')
    remark = generic.GenericRelation(Remark)

    def __unicode__(self):
        return u"{0} ({2} - {1})".format(self.name, self.composition, self.get_dosage_form_display())

    def natural_key(self):
            return (self.name, self.roa, self.dosage_form, self.composition)

    def order_info(self):
        """Outputs a string for Purchase application."""
        s = u"{0} {1} - {2} {3}".format(_("Dosage Form:"), self.get_dosage_form_display(), _("Composition:"), self.composition)
        return s

    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'roa', 'dosage_form', 'composition'),)


class Medicine(models.Model):
    """Stores a medicine object, "child" of :model:`inventory.Molecule`."""
    name = models.CharField(_("Name"), max_length=100)  # Brand Name. Example: Doliprane for INN Paracétamol
    exp_date = models.DateField(_("Expiration Date"))
    # Link to location
    location = models.ForeignKey(Location)
    # Fields for non-conformity compatibility
    nc_molecule = models.CharField(_("Non-conform Molecule"), max_length=100, blank=True, null=True)
    nc_composition = models.CharField(_("Non-conform Composition"), max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)
    # Common
    transactions = generic.GenericRelation(QtyTransaction)
    parent = models.ForeignKey(Molecule)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this medicine."""
        return self.transactions.aggregate(sum=models.Sum('value'))['sum']

    class Meta:
        ordering = ("exp_date", )


class MoleculeReqQty(models.Model):
    """Model for required quantity of a medicine"""
    allowance = models.ForeignKey('Allowance')
    base = models.ForeignKey('Molecule')
    required_quantity = models.IntegerField()


class EquipmentManager(models.Manager):
    """
    Manager for class Equipment.
    For deserialization purpose only.
    """
    def get_by_natural_key(self, name, packaging, consumable, perishable, group):
        return self.get(
            name=name,
            packaging=packaging,
            consumable=consumable,
            perishable=perishable,
            group=EquipmentGroup.objects.get_by_natural_key(name=group[0],),
            )

    def missing(self):
        """Returns the quantity to order to meet the requirement."""
        inventory_settings = Settings.objects.latest('id')
        exp_delay = utils.delay(inventory_settings.expire_date_warning_delay)
        # Selection of available ReqQty
        allowance_list = inventory_settings.allowance.all()
        req_qty_list = EquipmentReqQty.objects.filter(allowance__in=allowance_list).prefetch_related('base', 'allowance').order_by('base')
        # Equipement list
        equipment_list = Equipment.objects.filter(allowances__in=allowance_list).distinct().prefetch_related('article_set').order_by('name')
        # Article quantity transaction list
        qty_transaction_list = QtyTransaction.objects.filter(content_type=ContentType.objects.get_for_model(Article))

        result_list = []
        # Selection of the current quantities
        for equipment in equipment_list:
            current_qty = 0
            for article in equipment.article_set.all():
                # Do not add quantity if any non-conformity of article (near) expired.
                if article.nc_packaging or article.exp_date <= exp_delay:
                    continue
                # Add quantity for other ones
                for transaction in qty_transaction_list:
                    if transaction.object_id == article.id:
                        current_qty += transaction.value

            # Then, parse required quantities
            required_qty = utils.req_qty_element(equipment, req_qty_list)

            # Finally, add the equipment with new attribute if current < required
            if current_qty < required_qty:
                equipment.missing = (required_qty - current_qty)
                result_list.append(equipment)

        return result_list


class Equipment(models.Model):
    """Model for medical equipment."""
    objects = EquipmentManager()  # For deserialization

    name = models.CharField(max_length=100)  # Example: Nébulisateur
    packaging = models.CharField(max_length=100)  # Example: 1000 mg
    group = models.ForeignKey(EquipmentGroup)
    tag = models.ManyToManyField(Tag, blank=True)
    consumable = models.BooleanField(default=False)
    perishable = models.BooleanField(default=False)
    allowances = models.ManyToManyField(Allowance, through='EquipmentReqQty')
    remark = generic.GenericRelation(Remark)
    picture = models.ImageField(upload_to=utils.filepath, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
            return (self.name, self.packaging, self.consumable, self.perishable, self.group.natural_key())

    def order_info(self):
        """Outputs a string for Purchase application."""
        s = u"{0} {1}".format(_("Packaging:"), self.packaging)
        return s

    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'packaging', 'consumable', 'perishable', 'group'),)


class Article(models.Model):
    """Article model, "child" of Equipment."""
    name = models.CharField(_("Name"), max_length=100)  # Brand Name. Example: Coalgan
    exp_date = models.DateField(_("Expiration Date"), blank=True, null=True)
    # Link to location
    location = models.ForeignKey(Location)
    # Fields for non-conformity compatibility
    nc_packaging = models.CharField(_("Non-conform Packaging"), max_length=100, blank=True, null=True)
    # Field to simplify SQL requests when qty=0
    used = models.BooleanField(default=False)
    # Common
    transactions = generic.GenericRelation(QtyTransaction)
    parent = models.ForeignKey(Equipment)

    def __unicode__(self):
        return u"{0} (exp: {1})".format(self.name, self.exp_date)

    def get_quantity(self):
        """Computes the quantity according to the transactions attached to this medicine."""
        return self.transactions.aggregate(sum=models.Sum('value'))['sum']

    class Meta:
        ordering = ("exp_date", )


class EquipmentReqQty(models.Model):
    """Model for required quantity of a medical equipment"""
    allowance = models.ForeignKey('Allowance')
    base = models.ForeignKey('Equipment')
    required_quantity = models.IntegerField()


class Settings(models.Model):
    """Application settings."""
    allowance = models.ManyToManyField(Allowance, verbose_name=_('Allowance'))
    expire_date_warning_delay = models.PositiveIntegerField(_("Warning Delay for Expiration Dates"))
