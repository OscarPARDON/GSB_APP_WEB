from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.hashers import check_password

from DjangoProject1.asgi import application
from .models import Publication
from candidate.models import Application
from .forms import ApplicationForm
from datetime import datetime
##############################################################################################################

# This test the application view
class ApplicationTest(TestCase):

    def setUp(self): # Set up the test environnement
        self.client = Client() # Create the test client
        self.job_post = Publication.objects.create(id=1,title="TEST",description="Test", created_by_id=1) # Create a test publication for the test applications
        self.valid_url = reverse('application') + "?postID=1" # Application URL to send the test form

    def test_postID_error(self): # Test if the view has the right redirection when an invalid post ID is sent
        response = self.client.get(reverse('application')) # Get the HTTP status when no post id is sent
        self.assertEqual(response.status_code, 302) # Verify that the HTTP status is redirection (302)
        self.assertRedirects(response, '/') # Verify that the view redirect to the main page as expected

    def test_valid_application(self): # 
        # Créer des fichiers de test directement en mémoire
        cv_content = b'some cv content'  # Contenu binaire du fichier
        cover_letter_content = b'some cover letter content'  # Contenu binaire du fichier

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf")
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf")

        # Combinez les données et les fichiers dans UN SEUL dictionnaire
        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,  # Ajoutez les fichiers directement dans le dictionnaire data
            "cover_letter": cover_letter_file  # Ajoutez les fichiers directement dans le dictionnaire data
        }

        # Envoyez une seule requête POST
        response = self.client.post(self.valid_url, data)

        # Vérifications
        self.assertEqual(Application.objects.all().count(), 1)

        application = Application.objects.first()
        self.assertEqual(application.candidate_firstname, 'Jean')
        self.assertEqual(application.candidate_lastname, 'DUPONT')
        self.assertEqual(application.candidate_mail, 'jean.dupont@example.com')
        self.assertTrue(
            check_password('Caracas5360?', application.candidate_password))  # J'ai corrigé le mot de passe ici
        self.assertEqual(response.status_code, 302)

    def test_duplicate_application(self):
        Application.objects.create(
            application_number="20240301001",
            candidate_firstname="Jean",
            candidate_lastname="DUPONT",
            candidate_mail="other.mail@example.com",
            candidate_phone="0601020304",
            candidate_password="<PASSWORD>",
            job_publication=self.job_post,
            status=1,
        )

        cv_content = b'some cv content'
        cover_letter_content = b'some cover letter content'

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf")
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf")

        # Tous les données et fichiers dans un seul dictionnaire
        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,
            "cover_letter": cover_letter_file
        }

        response = self.client.post(self.valid_url, data)
        self.assertEqual(Application.objects.filter(candidate_lastname="DUPONT", candidate_firstname="Jean").count(), 1)
        self.assertRedirects(response, '/?error=Vous avez déja candidaté pour cette offre')

    def test_duplicate_email_application(self):
        Application.objects.create(
            application_number="20240301001",
            candidate_firstname="Other",
            candidate_lastname="NAME",
            candidate_mail="jean.dupont@example.com",
            candidate_phone="0601020304",
            candidate_password="<PASSWORD>",
            job_publication=self.job_post,
            status=1,
        )

        cv_content = b'some cv content'
        cover_letter_content = b'some cover letter content'

        cv_file = SimpleUploadedFile("cv.pdf", cv_content, content_type="application/pdf")
        cover_letter_file = SimpleUploadedFile("coverletter.pdf", cover_letter_content, content_type="application/pdf")

        # Tous les données et fichiers dans un seul dictionnaire
        data = {
            "firstname": "Jean",
            "name": "DUPONT",
            "email": "jean.dupont@example.com",
            "phone": "0601020304",
            "password": "Caracas5360?",
            "confirm": "Caracas5360?",
            "cv": cv_file,
            "cover_letter": cover_letter_file
        }

        response = self.client.post(self.valid_url, data)
        self.assertEqual(Application.objects.all().count(), 1)
        self.assertRedirects(response, '/?error=Vous avez déja candidaté pour cette offre')
