from dnacentersdk import api
from argparse import ArgumentParser
import csv
import os
import sys
import urllib3

urllib3.disable_warnings()


class SiteCache:
    def __init__(self, dnac_login):
        self._cache = {}
        sites = dnac_login.sites.get_site()
        for site in sites.response:
            self._cache[site.siteNameHierarchy] = site.id

    def lookup(self, sitename):
        if sitename in self._cache:
            return self._cache[sitename]
        else:
            raise ValueError("Cannot find site:{}".format(sitename))


class ImageCache:
    def __init__(self, dnac_login):
        self._cache = {}
        images = dnac_login.software_image_management_swim.get_software_image_details()
        for image in images.response:
            self._cache[image.name] = image.imageUuid

    def lookup(self, imagename):
        if imagename in self._cache:
            return self._cache[imagename]
        else:
            raise ValueError("Cannot find image:{}".format(imagename))


class TemplateCache:
    def __init__(self, dnac_login):
        self._cache = {}
        templates = dnac_login.configuration_templates.gets_the_templates_available()
        for template in templates:
            self._cache[template.name] = template.templateId

    def lookup(self, templatename):
        if templatename in self._cache:
            return self._cache[templatename]
        else:
            raise ValueError("Cannot find template:{}".format(templatename))


class DeviceCache:
    def __init__(self, dnac_login):
        self._cache = {}
        pnpdevices = dnac_login.device_onboarding_pnp.get_device_list()
        for pnp in pnpdevices:
            self._cache[pnp.deviceInfo.serialNumber] = pnp.id

    def lookup(self, deviceserial):
        if deviceserial in self._cache:
            return self._cache[deviceserial]
        else:
            raise ValueError("Cannot find device in PnP:{}".format(deviceserial))


def get_template(dnac_login, config_id, user_params):
    params = []
    template_variables = dnac_login.configuration_templates.get_template_details(config_id)
    for parameters in template_variables.templateParams:
        name = parameters['parameterName']
        params.append({"key": name, "value": user_params[name]})
    return params


def claim_devices(dnac_login, site_cache, image_cache, template_cache, devices_list):
    f = open(devices_list, 'rt')
    try:
        devices = csv.DictReader(f)
        for device in devices:
            try:
                device_id = device_cache.lookup(device['serial'])
                site_id = site_cache.lookup(device['siteName'])
                config_id = template_cache.lookup(device['templateName'])
                if 'image' in device and device['image'] != '':
                    image_id = image_cache.lookup(device['image'])
                else:
                    image_id = ''
            except ValueError as e:
                print("###ERROR {},{}: {}".format(device['name'], device['serial'], e))
                continue
            params = get_template(dnac_login, config_id, device)
            if 'topOfStack' in device:
                top_of_stack = device['topOfStack']
                device_type = "StackSwitch"
                payload = {
                    "imageInfo": {"imageId": image_id, "skip": False},
                    "configInfo": {"configId": config_id, "configParameters": params},
                    "topOfStackSerialNumber": top_of_stack
                }
            else:
                device_type = "Default"
                payload = {
                    "imageInfo": {"imageId": image_id, "skip": False},
                    "configInfo": {"configId": config_id, "configParameters": params}
                }

            claim_status = dnac_login.device_onboarding_pnp.claim_a_device_to_a_site(deviceId=device_id, siteId=site_id,
                                                                                     type=device_type, payload=payload)
            if "Claimed" in claim_status:
                status = "PLANNED"
            else:
                status = "FAILED"
            print('Device:{} name:{} siteName:{} Status:{}'.format(device['serial'], device['name'], device['siteName'],
                                                                   status))
    finally:
        f.close()


if __name__ == "__main__":

    parser = ArgumentParser(description='Path to devices CSV file')
    parser.add_argument('devices', type=str, help='Devices to claim CSV file')
    args = parser.parse_args()
    claim_list = args.devices

    if not os.path.isfile(claim_list):
        print('The file specified does not exist')
        sys.exit()

    dnac = api.DNACenterAPI()
    device_cache = DeviceCache(dnac)
    sites_cache = SiteCache(dnac)
    images_cache = ImageCache(dnac)
    templates_cache = TemplateCache(dnac)

    print("Claiming devices on file:", claim_list)
    print("#####################################")
    # print("the device ID for SN is: {}".format(device_cache.lookup('FCW2011C0U1')))
    claim_devices(dnac, sites_cache, images_cache, templates_cache, claim_list)
