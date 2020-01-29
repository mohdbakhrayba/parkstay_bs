from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkstay.models import Booking, BookingInvoice
from parkstay import emails
from ledger.payments.models import Invoice

from datetime import timedelta, date, datetime
from decimal import Decimal as D
from ledger.payments.utils import systemid_check
import itertools

class Command(BaseCommand):
    help = 'Clear out any unpaid bookings that have lapsed'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('days_back', nargs='+', type=int)

    def handle(self, *args, **options):
        print ("RUNNING") 
        days_back = options['days_back'][0]
        #print (sys.argv[0])
        unmatch_invoices_to_booking = []      
        past_date = datetime.now() -timedelta(days_back)
        print (past_date)
        system_identifier=systemid_check(settings.PS_PAYMENT_SYSTEM_ID)
        invoices = Invoice.objects.filter(reference__startswith=system_identifier, created__gte=past_date)
     
         
        for i in invoices:
            if BookingInvoice.objects.filter(invoice_reference=i.reference).count() == 0:
               print ("Found "+str(i.reference))
               unmatch_invoices_to_booking.append({'reference': i.reference,'created': i.created, 'order_number': i.order_number, 'amount': i.amount})

        if len(unmatch_invoices_to_booking) > 0:   
             context = {
              "past_date": past_date,
              "invoices": unmatch_invoices_to_booking
             }
             email_list = []
             for email_to in settings.NOTIFICATION_EMAIL.split(","):
                    email_list.append(email_to)
             print ("SENDING EMAIL") 
             emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Invoices without a booking",context,'ps/email/missing_invoice_bookings.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)


