from proxycurl.asyncio import Proxycurl, do_bulk
import asyncio


proxycurl = Proxycurl()
person = asyncio.run(proxycurl.linkedin.person.get(
    linkedin_profile_url='https://www.linkedin.com/in/bhavikostwal/'
))
print('Person Result:', person)