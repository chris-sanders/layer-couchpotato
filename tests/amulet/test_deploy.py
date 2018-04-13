#!/usr/bin/python3

import pytest
import amulet
import requests
import time


@pytest.fixture(scope="module")
def deploy():
    deploy = amulet.Deployment(series='xenial')
    deploy.add('haproxy', charm='~chris.sanders/haproxy')
    deploy.expose('haproxy')
    deploy.add('couchpotato')
    deploy.configure('couchpotato', {'proxy-port': 80,
                                     'backup-location': '/tmp/couchpotato'})
    deploy.setup(timeout=900)
    deploy.sentry.wait()
    return deploy


@pytest.fixture(scope="module")
def haproxy(deploy):
    return deploy.sentry['haproxy'][0]


@pytest.fixture(scope="module")
def couchpotato(deploy):
    return deploy.sentry['couchpotato'][0]


class TestCouchpotato():

    def test_deploy(self, deploy):
        try:
            deploy.sentry.wait(timeout=300)
        except amulet.TimeoutError:
            raise

    def test_web_frontend(self, deploy, couchpotato):
        page = requests.get('http://{}:{}'.format(couchpotato.info['public-address'], 5050))
        assert page.status_code == 200
        print(page)

    def test_reverseproxy(self, deploy, couchpotato, haproxy):
        page = requests.get('http://{}:{}'.format(couchpotato.info['public-address'], 5050))
        assert page.status_code == 200
        deploy.relate('couchpotato:reverseproxy', 'haproxy:reverseproxy')
        time.sleep(15)
        page = requests.get('http://{}:{}/couchpotato'.format(haproxy.info['public-address'], 80))
        assert page.status_code == 200

    def test_actions(self, deploy, couchpotato):
        for action in couchpotato.action_defined():
            uuid = couchpotato.run_action(action)
            action_output = deploy.get_action_output(uuid, full_output=True)
            print(action_output)
            assert action_output['status'] == 'completed'
        # Restart so it's running not part of the test
        couchpotato.run_action('start')

    #     # test we can access over http
    #     # page = requests.get('http://{}'.format(self.unit.info['public-address']))
    #     # self.assertEqual(page.status_code, 200)
    #     # Now you can use self.d.sentry[SERVICE][UNIT] to address each of the units and perform
    #     # more in-depth steps. Each self.d.sentry[SERVICE][UNIT] has the following methods:
    #     # - .info - An array of the information of that unit from Juju
    #     # - .file(PATH) - Get the details of a file on that unit
    #     # - .file_contents(PATH) - Get plain text output of PATH file from that unit
    #     # - .directory(PATH) - Get details of directory
    #     # - .directory_contents(PATH) - List files and folders in PATH on that unit
    #     # - .relation(relation, service:rel) - Get relation data from return service
