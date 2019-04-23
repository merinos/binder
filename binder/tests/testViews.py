from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse

from binder import models


class GetTests(TestCase):

    """Unit Tests that exercise HTTP GET."""

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('testuser',
                                        'testuser@example.com',
                                        'testpassword')
        response = self.client.login(username='testuser',
                                     password='testpassword')


    def test_GetIndex(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_GetServerIndex(self):
        response = self.client.get(reverse("server_list"))
        self.assertEqual(response.status_code, 200)

    def test_GetInvalidServer(self):
        """Get a zone list for a server not in the database."""
        server_name = "unconfigured.server.net"
        response = self.client.get(reverse("server_zone_list",
                                           args=(server_name, )))
        self.assertEqual(response.status_code, 404)


class PostTests(TestCase):

    """Unit Tests that exercise HTTP POST."""

    def setUp(self):
        self.client = Client()
        models.BindServer(hostname="testserver.test.net",
                          control_port=1234).save()

        user = User.objects.create_user('testuser',
                                        'testuser@example.com',
                                        'testpassword')
        response = self.client.login(username='testuser',
                                     password='testpassword')

    def test_DeleteRecordInitial_Empty(self):
        """Ensure the initial deletion form works as expected with no RR list."""
        dns_server = "testserver.test.net"
        zone_name = "testzone1.test.net"
        response = self.client.post(reverse("delete_record",
                                            kwargs={'dns_server': dns_server,
                                                    'zone_name': zone_name}),
                                    {"rr_list": []}, follow=True)
        self.assertRedirects(response,
                             reverse("zone_list",
                                     kwargs={'dns_server': dns_server,
                                             'zone_name': zone_name}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at least one record for deletion.")


    def test_DeleteRecordInitial(self):
        """Ensure the initial deletion form works as expected with RRs mentioned."""
        dns_server = "testserver.test.net"
        zone_name = "testzone1.test.net"
        response = self.client.post(reverse("delete_record",
                                            kwargs={'dns_server': dns_server,
                                                    'zone_name': zone_name}),
                                            {"rr_list": ["2dcff9df64b200a8f9f57c03f861cc15cee071e2",
                                                         "2375e0b6f6469b1e70fbc1cd98a393f7f1de995d"]})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            '<input type="hidden" id="zone_name" name="zone_name" value="testzone1.test.net" />', html=True)
        self.assertContains(response,
                            '<input type="hidden" id="rr_list" name="rr_list" value="[&#39;2dcff9df64b200a8f9f57c03f861cc15cee071e2&#39;, &#39;2375e0b6f6469b1e70fbc1cd98a393f7f1de995d&#39;]"/>',
                            html=True)
        self.assertContains(response,
                            '<input type="hidden" id="dns_server" name="dns_server" value="testserver.test.net" />',
                            html=True)
