import os
import sys
import traceback

import requests
from bottle import route, run, response

host = os.environ['DIRIGERA_HUB_HOST']
authorization_code = os.environ['DIRIGERA_HUB_AUTHORIZATION_CODE']

requests.packages.urllib3.disable_warnings()


@route('/metrics')
def metrics():
    devices = requests.get(f'https://{host}:8443/v1/devices', headers={
        'Authorization': f'Bearer {authorization_code}'
    }, verify=False).json()

    metrics = []
    for device in devices:
        try:
            labels = {
                'device_id': device['id'],
                'name': device['attributes']['customName']
            }
            try:
                labels['room'] = device['room']['name']
            except:
                pass
            if device['deviceType'] == 'airPurifier':
                metrics.append({
                    'name': 'air_pm25',
                    'labels': labels,
                    'value': device['attributes']['currentPM25']
                })
                metrics.append({
                    'name': 'starkvind_fan_speed',
                    'labels': labels,
                    'value': device['attributes']['motorState']
                })
                metrics.append({
                    'name': 'starkvind_filter_lifetime_seconds',
                    'labels': labels,
                    'value': device['attributes']['filterLifetime'] * 60
                })
                metrics.append({
                    'name': 'starkvind_filter_elapsed_time_seconds',
                    'labels': labels,
                    'value': device['attributes']['filterElapsedTime'] * 60
                })
            if device['deviceType'] == 'environmentSensor':
                metrics.append({
                    'name': 'air_pm25',
                    'labels': labels,
                    'value': device['attributes']['currentPM25']
                })
                metrics.append({
                    'name': 'air_relative_humidity_percent',
                    'labels': labels,
                    'value': device['attributes']['currentRH']
                })
                metrics.append({
                    'name': 'air_temperature_celcius',
                    'labels': labels,
                    'value': device['attributes']['currentTemperature']
                })
                metrics.append({
                    'name': 'vindstyrka_voc_index',
                    'labels': labels,
                    'value': device['attributes']['vocIndex']
                })
            elif device['deviceType'] == 'outlet':
                metrics.append({
                    'name': 'outlet_state',
                    'labels': labels,
                    'value': int(device['attributes']['isOn'])
                })
                if device['attributes']['productCode'] == 'E2225':
                    metrics.append({
                        'name': 'outlet_amps',
                        'labels': labels,
                        'value': device['attributes']['currentAmps']
                    })
                    metrics.append({
                        'name': 'outlet_kwh',
                        'labels': labels,
                        'value': device['attributes']['totalEnergyConsumed']
                    })
                    metrics.append({
                        'name': 'outlet_voltage',
                        'labels': labels,
                        'value': device['attributes']['currentVoltage']
                    })
        except:
            print(traceback.format_exc(), file=sys.stderr)

    buffer = []
    buffer.append('# TYPE air_pm25 gauge')
    buffer.append('# TYPE air_relative_humidity_percent gauge')
    buffer.append('# TYPE air_temperature_celcius gauge')
    buffer.append('# TYPE outlet_amps gauge')
    buffer.append('# TYPE outlet_joules_total counter')
    buffer.append('# TYPE outlet_state gauge')
    buffer.append('# TYPE outlet_voltage gauge')
    buffer.append('# TYPE starkvind_fan_speed gauge')
    buffer.append('# TYPE starkvind_filter_elapsed_time_seconds counter')
    buffer.append('# TYPE starkvind_filter_lifetime_seconds gauge')
    buffer.append('# TYPE vindstryka_voc_index gauge')

    for metric in sorted(metrics, key=lambda x: x['name']):
        buffer.append(metric['name'] + '{' + ','.join(f'{k}="{v}"' for k, v in sorted(metric['labels'].items())) + '}' + ' ' + str(metric['value']))

    response.content_type = 'text/plain'
    return '\n'.join(buffer)


run(host='0.0.0.0', port=8080)
