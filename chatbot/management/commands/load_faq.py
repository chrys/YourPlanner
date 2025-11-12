# CHANGED: Custom management command to load FAQ data for VasiliasBot

from django.core.management.base import BaseCommand
from chatbot.models import FAQ

class Command(BaseCommand):
    help = 'Load FAQ data into the chatbot database'
    
    # CHANGED: Define sample FAQ data for wedding planner
    FAQ_DATA = [
        {
            'question': 'What services do you offer?',
            'answer': 'We offer comprehensive wedding planning services including venue selection, catering, photography, decorations, and complete event coordination.',
            'order': 1,
        },
        {
            'question': 'How far in advance should I book your services?',
            'answer': 'We recommend booking at least 6-12 months before your wedding date to ensure availability and the best selection of vendors.',
            'order': 2,
        },
        {
            'question': 'What is the typical duration of a wedding ceremony?',
            'answer': 'The average wedding ceremony lasts 30-45 minutes, depending on your chosen officiant and traditions.',
            'order': 3,
        },
        {
            'question': 'Do you offer custom packages?',
            'answer': 'Yes, we can customize any package to fit your specific needs, preferences, and budget. Contact us for a personalized consultation.',
            'order': 4,
        },
        {
            'question': 'What is your cancellation policy?',
            'answer': 'Cancellations made 30 days or more before the event receive a full refund. Otherwise, a 50% cancellation fee applies.',
            'order': 5,
        },
        {
            'question': 'What payment methods do you accept?',
            'answer': 'We accept credit cards, bank transfers, PayPal, and offer flexible installment plans for your convenience.',
            'order': 6,
        },
        {
            'question': 'Can you help with destination weddings?',
            'answer': 'Absolutely! We have experience with destination weddings and can assist with logistics, vendor coordination, and on-site planning.',
            'order': 7,
        },
        {
            'question': 'How many weddings do you handle per year?',
            'answer': 'We focus on quality over quantity and typically coordinate 20-30 weddings per year to ensure personalized attention for each couple.',
            'order': 8,
        },
        {
            'question': 'Do you provide day-of coordination?',
            'answer': 'Yes, we offer complete day-of coordination services including timeline management, vendor coordination, and on-site problem solving.',
            'order': 9,
        },
        {
            'question': 'What is the typical cost of your services?',
            'answer': 'Pricing varies based on the scope of services and your budget. Full planning typically ranges from 10-15% of your total wedding budget.',
            'order': 10,
        },
    ]
    
    def handle(self, *args, **options):
        # CHANGED: Check if FAQ entries already exist
        existing_count = FAQ.objects.count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'{existing_count} FAQ entries already exist. Skipping FAQ load to avoid duplicates.'
                )
            )
            return
        
        # CHANGED: Create FAQ entries from data
        created_count = 0
        try:
            for faq_data in self.FAQ_DATA:
                faq = FAQ.objects.create(
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    order=faq_data['order'],
                    is_active=True,
                )
                created_count += 1
            
            # CHANGED: Output success message
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} FAQ entries'
                )
            )
        except Exception as e:
            # CHANGED: Output error message
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating FAQ entries: {str(e)}'
                )
            )
