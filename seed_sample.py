#!/usr/bin/env python
"""Seed a sample Contract Agreement + paid Invoice (with Receipt) to preview.

Run: python seed_sample.py
Safe to re-run: existing demo data is skipped, not duplicated.
"""
import os, sys
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
from apps.clients.models import Client
from apps.projects.models import Project
from apps.contracts.models import Contract
from apps.invoices.models import Invoice, InvoiceItem, Payment

DEMO_EMAIL = 'demo.client@example.com'


def main():
    admin = User.objects.filter(is_superuser=True).order_by('id').first()
    if not admin:
        admin = User.objects.filter(is_active=True).order_by('id').first()
    if not admin:
        print("ERROR: No user found to attach records to. Create a user first.")
        return

    # 1. Client
    client, created = Client.objects.get_or_create(
        email=DEMO_EMAIL,
        defaults={
            'full_name': 'James Mwangi',
            'company_name': 'Mwangi Family Trust',
            'phone': '+254 722 123 456',
            'address': 'Roysambu, Nairobi, Kenya',
            'kra_pin': 'A001234567Z',
        },
    )
    print(f"Client: {'created' if created else 'exists'} - {client.full_name}")

    # 2. Project
    project, created = Project.objects.get_or_create(
        name='Mwangi Residence - Roysambu',
        defaults={
            'client': client,
            'description': 'Design and construction of a 4-bedroom stone masonry residence including foundation, masonry, roofing, plastering, electrical and plumbing works.',
            'location': 'Roysambu, Nairobi',
            'start_date': date(2026, 8, 1),
            'end_date': date(2026, 12, 1),
            'budget': Decimal('5000000.00'),
            'status': 'Ongoing',
            'progress_percent': 25,
            'created_by': admin,
        },
    )
    print(f"Project: {'created' if created else 'exists'} - {project.name}")

    # 3. Contract (Signed)
    contract, created = Contract.objects.get_or_create(
        contract_number='CTR-2026-DEMO',
        defaults={
            'client': client,
            'project': project,
            'title': 'Construction of Mwangi Residence',
            'description': project.description,
            'terms': (
                '1. The Client shall pay a 30% deposit upon signing this agreement.\n'
                '2. The balance shall be paid in milestone installments as certified by the Engineer.\n'
                '3. Any variation to the scope shall be confirmed in writing and priced accordingly.\n'
                '4. The Contractor shall warrant the works for a period of 6 months after completion.\n'
                '5. The Client shall not employ subcontractors directly without the Contractor\u2019s consent.\n'
                '6. This agreement is governed by the laws of the Republic of Kenya.'
            ),
            'contract_amount': Decimal('5000000.00'),
            'deposit_percent': Decimal('30.00'),
            'start_date': date(2026, 8, 1),
            'end_date': date(2026, 12, 1),
            'status': 'Signed',
            'client_signature_name': 'James Mwangi',
            'signed_at': timezone.now(),
            'notes': 'Demo contract seeded for preview.',
            'created_by': admin,
        },
    )
    print(f"Contract: {'created' if created else 'exists'} - {contract.contract_number}")

    # 4. Invoice with items
    invoice, created = Invoice.objects.get_or_create(
        invoice_number='INV-2026-DEMO',
        defaults={
            'client': client,
            'project': project,
            'date': date(2026, 7, 31),
            'due_date': date(2026, 8, 15),
            'status': 'Paid',
            'subtotal': Decimal('1500000.00'),
            'tax_percent': Decimal('0.00'),
            'tax_amount': Decimal('0.00'),
            'discount': Decimal('0.00'),
            'grand_total': Decimal('1500000.00'),
            'amount_paid': Decimal('1500000.00'),
            'balance': Decimal('0.00'),
            'notes': '30% deposit per Contract CTR-2026-DEMO.',
            'created_by': admin,
        },
    )
    if created:
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Deposit - Construction of Mwangi Residence (30% of KSh 5,000,000)',
            quantity=1,
            unit='lump sum',
            unit_price=Decimal('1500000.00'),
        )
    print(f"Invoice: {'created' if created else 'exists'} - {invoice.invoice_number}")

    # 5. Payment (this generates the receipt)
    payment, created = Payment.objects.get_or_create(
        invoice=invoice,
        amount=Decimal('1500000.00'),
        payment_date=date(2026, 7, 31),
        payment_method='Bank Transfer',
        reference='MPESA-WXC8JQ9F2L',
        recorded_by=admin,
        defaults={'notes': 'Deposit payment per Contract CTR-2026-DEMO.'},
    )
    if created and not payment.receipt_number:
        payment.save()
    print(f"Payment: {'created' if created else 'exists'} - {payment.receipt_number or payment.reference}")

    print()
    print("=" * 60)
    print("  SAMPLE DATA READY")
    print("=" * 60)
    print(f"  Contract:  {contract.contract_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/contracts/")
    print(f"    Print:   https://schones-heim-builders.co.ke/contracts/{contract.pk}/pdf/")
    print(f"  Invoice:   {invoice.invoice_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/invoices/")
    print(f"  Receipt:   {payment.receipt_number}")
    print(f"    View:    https://schones-heim-builders.co.ke/invoices/receipt/{payment.pk}/")
    print("=" * 60)


if __name__ == '__main__':
    main()
