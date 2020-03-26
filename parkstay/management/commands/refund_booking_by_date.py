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
        bookings = Booking.objects.filter(arrival__gte='2019-08-01', arrival__lte='2019-08-01')[:20]
        booking_refunds = []

        for b in bookings:
           print (b.created)
           bookinginvoice = BookingInvoice.objects.filter(booking=b)
           for bi in bookinginvoice:
                print (bi.invoice_reference)
                invoices = Invoice.objects.filter(reference=bi.invoice_reference)
                invoice_string = ""
                for inv in invoices:
                    invoice_string = invoice_string + inv.reference+"," 
                    if  inv.bpoint_transactions.count() == 1:
                        for bp in inv.bpoint_transactions:
                            if bp.action == 'payment':
                                bpoint_id = bp.id
                                # call ledger refund command (with try catch)      
                    else:
                        print ("Too many transactions")

           booking_refunds.append({'booking_id': b.id, 'booking_customer': b.customer.email, 'invcoies': invoice_string })
           print ("-----")

        # Send email with success and failed refunds 
        print (days_back)
        print (booking_refunds)
        print ("COMPLETED")  
        return True
        #print (sys.argv[0])
#        unmatch_invoices_to_booking = []      
#        past_date = datetime.now() -timedelta(days_back)
#        print (past_date)
#        system_identifier=systemid_check(settings.PS_PAYMENT_SYSTEM_ID)
#        invoices = Invoice.objects.filter(reference__startswith=system_identifier, created__gte=past_date)
#     
#         
#        for i in invoices:
#            if BookingInvoice.objects.filter(invoice_reference=i.reference).count() == 0:
#               print ("Found "+str(i.reference))
#               unmatch_invoices_to_booking.append({'reference': i.reference,'created': i.created, 'order_number': i.order_number, 'amount': i.amount})
#
#        if len(unmatch_invoices_to_booking) > 0:   
#             context = {
#              "past_date": past_date,
#              "invoices": unmatch_invoices_to_booking
#             }
#             email_list = []
#             for email_to in settings.NOTIFICATION_EMAIL.split(","):
#                    email_list.append(email_to)
#             print ("SENDING EMAIL") 
#             emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Invoices without a booking",context,'ps/email/missing_invoice_bookings.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
#

