from dnacentersdk import api
import urllib3

urllib3.disable_warnings()
dnac = api.DNACenterAPI()


def get_all_templates():
    try:
        templates = dnac.configuration_templates.gets_the_templates_available()
        template_list = {}
        for template in templates:
            template_list[template.name] = template.templateId
        return template_list
    except ValueError as e:
        print('An error has occurred trying to fetch the Template list')
        return e


def get_all_images():
    try:
        images = dnac.software_image_management_swim.get_software_image_details()
        image_list = {}
        for image in images.response:
            image_list[image.name] = image.imageUuid
        return image_list
    except ValueError as e:
        print('An error has occurred trying to fetch the SW Image list')
        return e


def get_all_pnp_device():
    try:
        devices = dnac.device_onboarding_pnp.get_device_list()
        pnp_list = {}
        for device in devices:
            if device.deviceInfo.siteClaimType != "Sensor":
                pnp_list[device.deviceInfo.serialNumber] = {}
                pnp_list[device.deviceInfo.serialNumber]['pid'] = device.deviceInfo.pid
                pnp_list[device.deviceInfo.serialNumber]['state'] = device.deviceInfo.state
                pnp_list[device.deviceInfo.serialNumber]['image'] = device.deviceInfo.imageVersion
                pnp_list[device.deviceInfo.serialNumber]['stack'] = device.deviceInfo.stack
        return pnp_list
    except ValueError as e:
        print('An error has occurred trying to fetch the PnP device list')
        return e
