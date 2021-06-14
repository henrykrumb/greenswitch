#!/usr/bin/env python
# -*- coding: utf-8 -*-

from textwrap import dedent
import unittest

from greenswitch.esl import ESLEvent


class TestESLEventParser(unittest.TestCase):
    def test_parse_a_simple_event(self):
        event_plain = dedent("""\
            Event-Name: HEARTBEAT
            Core-UUID: cb2d5146-9a99-11e4-9291-092b1a87b375
            FreeSWITCH-Hostname: evoluxdev
            FreeSWITCH-Switchname: freeswitch
            FreeSWITCH-IPv4: 172.16.7.47
            FreeSWITCH-IPv6: %3A%3A1""")

        event = ESLEvent(event_plain)
        self.assertEqual(len(event.headers.keys()), 6)

    def test_parse_a_event_with_content(self):
        event_plain = dedent("""\
            Content-Type: log/data
            Content-Length: 126
            Log-Level: 7
            Text-Channel: 3
            Log-File: switch_core_state_machine.c
            Log-Func: switch_core_session_destroy_state
            Log-Line: 710
            User-Data: 4c882cc4-cd02-11e6-8b82-395b501876f9

            2016-12-28 10:34:08.398763 [DEBUG] switch_core_state_machine.c:710 (sofia/internal/7071@devitor) State DESTROY going to sleep""")

        event = ESLEvent(event_plain)
        self.assertEqual(len(event.headers.keys()), 8)
        length = int(event.headers['Content-Length'])
        self.assertEqual(event_plain[217:217 + length],
                         '2016-12-28 10:34:08.398763 [DEBUG] switch_core_state_machine.c:710 (sofia/internal/7071@devitor) State DESTROY going to sleep')

    def test_parse_a_event_where_the_value_is_multiline(self):
        event_plain = dedent("""\
            variable_switch_r_sdp: v=0
            o=- 3631463817 3631463817 IN IP4 172.16.7.70
            s=pjmedia
            b=AS:84
            t=0 0
            a=X-nat:0
            m=audio 4016 RTP/AVP 103 102 104 109 3 0 8 9 101
            c=IN IP4 172.16.7.70
            b=AS:64000
            a=rtpmap:103 speex/16000
            a=rtpmap:102 speex/8000
            a=rtpmap:104 speex/32000
            a=rtpmap:109 iLBC/8000
            a=fmtp:109 mode=30
            a=rtpmap:3 GSM/8000
            a=rtpmap:0 PCMU/8000
            a=rtpmap:8 PCMA/8000
            a=rtpmap:9 G722/8000
            a=rtpmap:101 telephone-event/8000
            a=fmtp:101 0-15
            a=rtcp:4017 IN IP4 172.16.7.70

            variable_endpoint_disposition: DELAYED NEGOTIATION""")

        event = ESLEvent(event_plain)

        expected_variable_value = dedent("""\
            v=0
            o=- 3631463817 3631463817 IN IP4 172.16.7.70
            s=pjmedia
            b=AS:84
            t=0 0
            a=X-nat:0
            m=audio 4016 RTP/AVP 103 102 104 109 3 0 8 9 101
            c=IN IP4 172.16.7.70
            b=AS:64000
            a=rtpmap:103 speex/16000
            a=rtpmap:102 speex/8000
            a=rtpmap:104 speex/32000
            a=rtpmap:109 iLBC/8000
            a=fmtp:109 mode=30
            a=rtpmap:3 GSM/8000
            a=rtpmap:0 PCMU/8000
            a=rtpmap:8 PCMA/8000
            a=rtpmap:9 G722/8000
            a=rtpmap:101 telephone-event/8000
            a=fmtp:101 0-15
            a=rtcp:4017 IN IP4 172.16.7.70""")

        self.assertEqual(
            event.headers['variable_switch_r_sdp'],
            expected_variable_value)
        self.assertTrue(
            'variable_endpoint_disposition' in event.headers)

    def test_fixes_issue_54(self):
        event_plain = dedent("""\
                Event-Subclass: sofia::notify_refer
                Event-Name: CUSTOM
                Core-UUID: c6327c82-be80-4c4d-8966-2a11bb4004f4
                FreeSWITCH-Hostname: PBX-SIPT-IPSM-2
                FreeSWITCH-Switchname: PBX-SIPT-IPSM-2
                FreeSWITCH-IPv4: 192.168.194.31
                FreeSWITCH-IPv6: ::1
                Event-Date-Local: 2020-03-13 10:52:49
                Event-Date-GMT: Fri, 13 Mar 2020 14:52:49 GMT
                Event-Date-Timestamp: 1584111169386681
                Event-Calling-File: sofia.c
                Event-Calling-Function: sofia_handle_sip_i_notify
                Event-Calling-Line-Number: 657
                Event-Sequence: 895854
                content-type: message/sipfrag
                event-package: refer
                event-id: 17501791
                contact: +14167601210@10.1.109.13
                from: +14167601210@hipv.itech.ca
                from-tag: 1400489415-1584111124103
                to: 6137700001@hipv.itech.ca
                to-tag: Njryg7ra0U9vN
                call-id: 225c8744-dfdd-1238-6da5-005056a17d9b
                subscription-substate: terminated
                subscription-reason: noresource
                UniqueID: 63509455-96e6-4e43-b52f-8239e7088331
                Content-Length: 20
                Content-Length: 20

                SIP/2.0 100 Trying""")

        event = ESLEvent(event_plain)

        self.assertEqual(event.headers['Content-Length'], '20')
