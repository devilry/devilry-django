from utils import AssignmentSync, Command


class ListAssignmentGroups(Command):
    name = 'list-assignment-groups'
    description = 'List assignment groups on a given assignment.'
    args_help = '<assignment-id>'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        self.validate_argslen(1)
        server = self.get_server()
        assignment_id = int(self.args[0])
        groups = server.list_assignmentgroups(assignment_id)
        for group in groups:
            print "%15d : %s (%d deliveries)" % (group['id'],
                    ', '.join(group['students']),
                    group['number_of_deliveries'])


class GetDeliveries(Command):
    name = 'get-deliveries'
    description = 'Get deliveries.'
    urlpath = '/xmlrpc_examiner/'

    def command(self):
        AssignmentSync(self.get_cookiepath(), self.get_server(),
                self.get_url())
