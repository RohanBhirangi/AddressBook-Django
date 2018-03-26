import os, sys
import unittest
from elasticsearch import Elasticsearch
import time

sys.path.append(os.getcwd())

import config
from datastore import elasticsearch_handler

host = config.elasticsearch_host
port = config.elasticsearch_port
es = Elasticsearch(host + ":" + port + "/")


class TestInsertContact(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global es
        es.indices.create(index='addressbook', ignore=400)

    @classmethod
    def tearDown(cls):
        global es
        es.indices.delete(index="addressbook", ignore=[400, 404])

    def test_insert_pass(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        elasticsearch_handler.insert_contact(data)
        time.sleep(1)
        results = es.search(index="addressbook", doc_type="contact", body={"query": {"match": {"name": data["name"]}}})
        inserted_data = results["hits"]["hits"][0]["_source"]
        self.assertEqual(data["name"], inserted_data["name"])
        self.assertEqual(data["number"], inserted_data["number"])
        self.assertEqual(data["address"], inserted_data["address"])
        self.assertEqual(data["email"], inserted_data["email"])

    def test_insert_contact_exists(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "John", "number": "0987654321", "address": "Wine Road, Apple, CD",
                    "email": "john@gmail.com"}
        response = elasticsearch_handler.insert_contact(new_data)
        self.assertFalse(response["acknowledged"])

    def test_insert_invalid_name(self):
        data = {"name": "JohnDaveMikePaulKurtS", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.insert_contact(data)
        self.assertFalse(response["acknowledged"])

    def test_insert_invalid_number(self):
        data = {"name": "John", "number": "1234567890123456", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.insert_contact(data)
        self.assertFalse(response["acknowledged"])

    def test_insert_invalid_address(self):
        data = {"name": "John", "number": "1234567890",
                "address": "Maple Road, Orange, AB, Maple Road, Orange, AB, Maple Road, Orange, AB, Maple Road, Orange,"
                           "AB, Maple Road, Orange, AB, Maple Road, Orange, AB", "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.insert_contact(data)
        self.assertFalse(response["acknowledged"])

    def test_insert_invalid_email(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe#gmail,com"}
        response = elasticsearch_handler.insert_contact(data)
        self.assertFalse(response["acknowledged"])


class TestGetContact(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global es
        es.indices.create(index='addressbook', ignore=400)

    @classmethod
    def tearDown(cls):
        global es
        es.indices.delete(index="addressbook", ignore=[400, 404])

    def test_get_pass(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        results = elasticsearch_handler.get_contact(data["name"])
        get_data = results[0]["_source"]
        self.assertEqual(data["name"], get_data["name"])
        self.assertEqual(data["number"], get_data["number"])
        self.assertEqual(data["address"], get_data["address"])
        self.assertEqual(data["email"], get_data["email"])

    def test_get_fail(self):
        test_name = "Paul"
        results = elasticsearch_handler.get_contact(test_name)
        self.assertEqual(0, len(results))


class TestUpdateContact(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global es
        es.indices.create(index='addressbook', ignore=400)

    @classmethod
    def tearDown(cls):
        global es
        es.indices.delete(index="addressbook", ignore=[400, 404])

    def test_update_pass(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "Johnny", "number": "0987654321", "address": "Wine Road, Apple, CD",
                    "email": "johnny@gmail.com"}
        elasticsearch_handler.update_contact("John", new_data)
        time.sleep(1)
        results = es.search(index="addressbook", doc_type="contact",
                            body={"query": {"match": {"name": new_data["name"]}}})
        updated_data = results["hits"]["hits"][0]["_source"]
        self.assertEqual(new_data["name"], updated_data["name"])
        self.assertEqual(new_data["number"], updated_data["number"])
        self.assertEqual(new_data["address"], updated_data["address"])
        self.assertEqual(new_data["email"], updated_data["email"])

    def test_update_contact_exists(self):
        data1 = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                 "email": "johndoe@gmail.com"}
        data2 = {"name": "Mark", "number": "7264527893", "address": "Scope Road, Peach, EF",
                 "email": "mark@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data1)
        es.index(index="addressbook", doc_type="contact", id=2, body=data2)
        time.sleep(1)
        new_data = {"name": "Mark", "number": "0987654321", "address": "Wine Road, Apple, CD",
                    "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.update_contact("John", new_data)
        self.assertFalse(response["acknowledged"])

    def test_update_invalid_name(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "JohnDaveMikePaulKurtS", "number": "1234567890", "address": "Maple Road, Orange, AB",
                    "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.update_contact("John", new_data)
        self.assertFalse(response["acknowledged"])

    def test_update_invalid_number(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "John", "number": "1234567890123456", "address": "Maple Road, Orange, AB",
                    "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.update_contact("John", new_data)
        self.assertFalse(response["acknowledged"])

    def test_update_invalid_address(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "John", "number": "1234567890",
                    "address": "Maple Road, Orange, AB, Maple Road, Orange, AB, Maple Road, Orange, AB, Maple Road,"
                               "Orange," "AB, Maple Road, Orange, AB, Maple Road, Orange, AB",
                    "email": "johndoe@gmail.com"}
        response = elasticsearch_handler.update_contact("John", new_data)
        self.assertFalse(response["acknowledged"])

    def test_update_invalid_email(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        new_data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                    "email": "johndoe#gmail,com"}
        response = elasticsearch_handler.update_contact("John", new_data)
        self.assertFalse(response["acknowledged"])


class TestDeleteContact(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global es
        es.indices.create(index='addressbook', ignore=400)

    @classmethod
    def tearDown(cls):
        global es
        es.indices.delete(index="addressbook", ignore=[400, 404])

    def test_delete_pass(self):
        data = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                "email": "johndoe@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data)
        time.sleep(1)
        elasticsearch_handler.delete_contact(data["name"])
        time.sleep(1)
        results = es.search(index="addressbook", doc_type="contact", body={"query": {"match": {"name": data["name"]}}})
        self.assertEqual(0, len(results["hits"]["hits"]))

    def test_delete_fail(self):
        test_name = "Paul"
        response = elasticsearch_handler.delete_contact(test_name)
        self.assertFalse(response["acknowledged"])


class TestGetContacts(unittest.TestCase):

    @classmethod
    def setUp(cls):
        global es
        es.indices.create(index='addressbook', ignore=400)

    @classmethod
    def tearDown(cls):
        global es
        es.indices.delete(index="addressbook", ignore=[400, 404])

    def test_get_contacts_pass(self):
        data1 = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                 "email": "johndoe@gmail.com"}
        data2 = {"name": "Mark", "number": "7264527893", "address": "Scope Road, Peach, EF",
                 "email": "mark@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data1)
        es.index(index="addressbook", doc_type="contact", id=2, body=data2)
        time.sleep(1)
        results = elasticsearch_handler.get_contacts(None, None, None)
        self.assertEqual(2, len(results))
        count = 0
        for result in results:
            get_data = result["_source"]
            if result["_id"] == "1":
                self.assertEqual(data1["name"], get_data["name"])
                self.assertEqual(data1["number"], get_data["number"])
                self.assertEqual(data1["address"], get_data["address"])
                self.assertEqual(data1["email"], get_data["email"])
                count += 1
            elif result["_id"] == "2":
                self.assertEqual(data2["name"], get_data["name"])
                self.assertEqual(data2["number"], get_data["number"])
                self.assertEqual(data2["address"], get_data["address"])
                self.assertEqual(data2["email"], get_data["email"])
                count += 1
        self.assertEqual(2, count)

    def test_get_contacts_fail(self):
        results = elasticsearch_handler.get_contacts(None, None, None)
        self.assertEqual(0, len(results))

    def test_page_size(self):
        data1 = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                 "email": "johndoe@gmail.com"}
        data2 = {"name": "Mark", "number": "7264527893", "address": "Scope Road, Peach, EF",
                 "email": "mark@gmail.com"}
        data3 = {"name": "Paul", "number": "5162763528", "address": "Neon Road, Berry, GH",
                 "email": "paul@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data1)
        es.index(index="addressbook", doc_type="contact", id=2, body=data2)
        es.index(index="addressbook", doc_type="contact", id=3, body=data3)
        time.sleep(1)
        results = elasticsearch_handler.get_contacts(2, None, None)
        self.assertEqual(2, len(results))

    def test_page(self):
        data1 = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                 "email": "johndoe@gmail.com"}
        data2 = {"name": "Mark", "number": "7264527893", "address": "Scope Road, Peach, EF",
                 "email": "mark@gmail.com"}
        data3 = {"name": "Paul", "number": "5162763528", "address": "Neon Road, Berry, GH",
                 "email": "paul@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data1)
        es.index(index="addressbook", doc_type="contact", id=2, body=data2)
        es.index(index="addressbook", doc_type="contact", id=3, body=data3)
        time.sleep(1)
        results = elasticsearch_handler.get_contacts(None, 2, None)
        self.assertEqual(1, len(results))

    def test_query(self):
        data1 = {"name": "John", "number": "1234567890", "address": "Maple Road, Orange, AB",
                 "email": "johndoe@gmail.com"}
        data2 = {"name": "Mark", "number": "7264527893", "address": "Scope Road, Peach, EF",
                 "email": "mark@gmail.com"}
        data3 = {"name": "Paul", "number": "5162763528", "address": "Neon Road, Orange, GH",
                 "email": "paul@gmail.com"}
        es.index(index="addressbook", doc_type="contact", id=1, body=data1)
        es.index(index="addressbook", doc_type="contact", id=2, body=data2)
        es.index(index="addressbook", doc_type="contact", id=3, body=data3)
        time.sleep(1)
        results = elasticsearch_handler.get_contacts(None, None, "Orange")
        self.assertEqual(2, len(results))
        count = 0
        for result in results:
            get_data = result["_source"]
            if result["_id"] == "1":
                self.assertEqual(data1["name"], get_data["name"])
                self.assertEqual(data1["number"], get_data["number"])
                self.assertEqual(data1["address"], get_data["address"])
                self.assertEqual(data1["email"], get_data["email"])
                count += 1
            elif result["_id"] == "3":
                self.assertEqual(data3["name"], get_data["name"])
                self.assertEqual(data3["number"], get_data["number"])
                self.assertEqual(data3["address"], get_data["address"])
                self.assertEqual(data3["email"], get_data["email"])
                count += 1
        self.assertEqual(2, count)


if __name__ == '__main__':
    unittest.main()
