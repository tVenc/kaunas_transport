Vilniaus viešojo transporto (autobusai ir troleibusai) integraciją
Įdiegus per HACS pridėti prie integracijų ir bus pagal maršrutą sukuriami device_tracker

type: custom:auto-entities
card:
  type: map
  title: 3G Autobusai mieste
  hours_to_show: 0
  dark_mode: false
filter:
  include:
    - entity_id: device_tracker.vln_4g_*
      options:
        name: 4G
show_empty: true
