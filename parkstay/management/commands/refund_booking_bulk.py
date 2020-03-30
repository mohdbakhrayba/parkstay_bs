from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkstay.models import Booking, BookingInvoice
from parkstay import emails
from ledger.payments.models import Invoice
from ledger.accounts.models import EmailUser, Address, EmailIdentity
from ledger.payments.utils import systemid_check, update_payments

from datetime import timedelta, date, datetime
from decimal import Decimal as D
from ledger.payments.utils import systemid_check
from decimal import Decimal
import itertools

class Command(BaseCommand):
    help = 'Clear out any unpaid bookings that have lapsed'

    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('days_back', nargs='+', type=int)
        parser.add_argument('file',)

    def handle(self, *args, **options):
        print ("RUNNING")
        user = EmailUser.objects.get(email='jason.moore@dbca.wa.gov.au') 
        #days_back = options['days_back'][0]
        file_path = options['file']
        print (file_path)

        booking_refunds = []
        booking_errors = []
        refund_success = False

        #Booking.objects.filter(arrival__gte='2020-01-01', arrival__lte='2020-01-21')[:2]
        f = open(file_path)
        for line in f:
           line = line.strip('\n')
           print(line+":")
           
           try:
               b = Booking.objects.get(id=line)
               print (b) 
        #fo    r b in bookings:
               print (b.created)
               bookinginvoice = BookingInvoice.objects.filter(booking=b)
               for bi in bookinginvoice:
                    print (bi.invoice_reference)
                    invoices = Invoice.objects.filter(reference=bi.invoice_reference)
                    invoice_string = ""
                    bp_amount = "0.00"
                    for inv in invoices:
                        invoice_string = invoice_string + inv.reference+"," 
                        if  inv.bpoint_transactions.count() == 1:
                            for bp in inv.bpoint_transactions:
                                if bp.action == 'payment':
                                    bpoint_id = bp.id
                                    # call ledger refund command (with try catch)
                                    try:
                                        bp_amount = '{:.2f}'.format(float(bp.amount))
                                        #bpoint_money_to = (Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))) - Decimal('{:.2f}'.format(float(bp_txn['line-amount']))))
                                        #lines.append({'ledger_description':str("Payment Gateway Refund to "+bp_txn['txn_number']),"quantity":1,"price_incl_tax": bpoint_money_to,"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 3})
                                        #bpoint = BpointTransaction.objects.get(txn_number=bp_txn['txn_number'])
                                        info = {'amount': Decimal('{:.2f}'.format(float(bp.amount))), 'details' : 'Refund via system'}
                                        refund = bp.refund(info,user)
                                        refund_success = True 
                                        update_payments(bp.crn1)  
                                    except Exception as e:
                                        print (e)
                                        refund_success = False
                                        #bpoint_failed_amount = Decimal(bp_txn['line-amount'])
                                        #lines = []
                                        #lines.append({'ledger_description':str("Refund failed for txn "+bp_txn['txn_number']),"quantity":1,"price_incl_tax":bpoint_failed_amount,"oracle_code":str(settings.UNALLOCATED_ORACLE_CODE), 'line_status': 1})
      
                        else:
                            refund_success = False
                            print ("Too many transactions")
               booking_refunds.append({'booking_id': b.id, 'amount': bp_amount, 'booking_customer': b.customer.email, 'invoices': invoice_string, 'refund_success': refund_success })
           except Exception as e:
               print (e)
               booking_errors.append(line)
           print ("-----")

        # Send email with success and failed refunds 
        #print (days_back)
        print (booking_refunds)
        context = {
         "booking_refunds":booking_refunds,
         "booking_errors": booking_errors 
        }
        email_list = []
        for email_to in settings.NOTIFICATION_EMAIL.split(","):
               email_list.append(email_to)
        print ("SENDING EMAIL")


        emails.sendHtmlEmail(tuple(email_list),"[PARKSTAY] Bulk Refund Script",context,'ps/email/bulk_refund.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
        #print ("COMPLETED")  
        return "Completed"
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

