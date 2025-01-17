from django.test import TestCase, RequestFactory
from django.urls import reverse
from .views import get_tasks_list, check_task_status


class GetTasksListViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("tasks_list")

    def test_get_tasks_list_with_valid_page(self):

        request = self.factory.get(self.url, {"page": "1"})
        response = get_tasks_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks_list", response.context_data)
        self.assertEqual(len(response.context_data["tasks_list"]), 2)
        self.assertEqual(response.context_data["num_of_pages"], 1)
        self.assertEqual(response.context_data["current_page"], 1)

    def test_get_tasks_list_with_invalid_page(self):

        request = self.factory.get(self.url, {"page": "invalid"})
        response = get_tasks_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks_list", response.context_data)
        self.assertEqual(len(response.context_data["tasks_list"]), 2)
        self.assertEqual(response.context_data["num_of_pages"], 1)
        self.assertEqual(response.context_data["current_page"], 1)

    def test_get_tasks_list_without_page_param(self):

        request = self.factory.get(self.url)
        response = get_tasks_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("tasks_list", response.context_data)
        self.assertEqual(len(response.context_data["tasks_list"]), 2)
        self.assertEqual(response.context_data["num_of_pages"], 1)
        self.assertEqual(response.context_data["current_page"], 1)


class CheckTaskStatusViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse("check_task_status")

    def test_get_request_with_valid_task_id(self):
        request = self.factory.get(
            self.url, {"task_id": "df70b3eb-265b-44e1-bca1-1c641f7ba4a8"}
        )
        response = check_task_status(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("task_id", response.context_data)
        self.assertEqual(
            response.context_data["task_id"], "df70b3eb-265b-44e1-bca1-1c641f7ba4a8"
        )
        self.assertEqual(response.context_data["status"], "SUCCESS")
        self.assertEqual(response.context_data["result"], None)

    def test_get_request_with_exception_result(self):

        request = self.factory.get(
            self.url, {"task_id": "bf82cd11-27ce-46e7-9b24-2ca84858a23e"}
        )
        response = check_task_status(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("task_id", response.context_data)
        self.assertEqual(
            response.context_data["task_id"], "bf82cd11-27ce-46e7-9b24-2ca84858a23e"
        )
        self.assertEqual(response.context_data["status"], "FAILURE")
        self.assertEqual(response.context_data["result"], "Exception(error)")

    def test_get_request_with_invalid_task_id(self):

        request = self.factory.get(self.url)
        response = check_task_status(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["error"], "task not founded")
