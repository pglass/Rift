import uuid

from specter import DataSpec, expect, require, skip

from spec.rift.api.resources.fixtures import MockedDatabase
from spec.rift.api.datasets import VALID_TARGETS, INVALID_TARGETS


class TargetsResource(MockedDatabase):

    def can_list_targets(self):
        resp = self.app.get('/v1/tenant/targets')
        require(resp.status_int).to.equal(200)
        require(resp.json).to.contain('targets')
        expect(resp.json['targets']).to.equal([])

    def can_get_target(self):
        post_resp = self._post_target()
        target_id = post_resp.json['target_id']

        resp = self.app.get('/v1/tenant/targets/{0}'.format(target_id))
        require(resp.status_int).to.equal(200)
        expect(resp.json).to.contain('authentication')
        expect(resp.json).to.contain('address')
        expect(resp.json).to.contain('type')
        expect(resp.json).to.contain('id')
        expect(resp.json).to.contain('name')
        expect(resp.json['id']).to.equal(target_id)

    @skip('Fails - "not enough arguments for format string" in mongomock')
    def can_delete_target(self):
        post_resp = self._post_target()
        target_id = post_resp.json['target_id']

        url = '/v1/tenant/targets/{0}'.format(target_id)
        resp = self.app.delete(url)
        expect(resp.status_int).to.equal(200)

        resp = self.app.get(url, expect_errors=True)
        expect(resp.status_int).to.equal(404)

    def should_404_on_nonexistent_target(self):
        resp = self.app.get('/v1/tenant/targets/{0}'.format(uuid.uuid4()),
                            expect_errors=True)
        expect(resp.status_int).to.equal(404)

    def _post_target(self):
        resp = self.app.post_json(
            '/v1/tenant/targets',
            VALID_TARGETS['nova_target_with_rax_auth']['body'])
        require(resp.status_int).to.equal(201)
        require(resp.json).to.contain('target_id')
        return resp

    class SuccessfulPostRequests(MockedDatabase, DataSpec):
        DATASET = VALID_TARGETS

        def can_post(self, body):
            resp = self.app.post_json('/v1/tenant/targets', body)
            require(resp.status_int).to.equal(201)
            expect(resp.json).to.contain('target_id')

    class BadPostRequests(MockedDatabase, DataSpec):
        DATASET = INVALID_TARGETS

        def returns_400_on_a(self, body):
            resp = self.app.post_json('/v1/tenant/targets', body,
                                      expect_errors=True)
            expect(resp.status_int).to.equal(400)
