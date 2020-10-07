import * as React from 'react';
import { ChakraSelect } from 'app/components';

const buildLocations = networks => {
  const locations = [];
  networks.map(net => {
    const netLocations = [];
    net.locations.map(loc => {
      netLocations.push({
        label: loc.display_name,
        value: loc.name,
        group: net.display_name,
      });
    });
    locations.push({ label: net.display_name, options: netLocations });
  });
  return locations;
};

export const QueryLocation = ({ locations, onChange, label }) => {
  const options = buildLocations(locations);
  const handleChange = e => {
    const selected = [];
    e &&
      e.map(sel => {
        selected.push(sel.value);
      });
    onChange({ field: 'query_location', value: selected });
  };
  return (
    <ChakraSelect
      isMulti
      size="lg"
      options={options}
      aria-label={label}
      name="query_location"
      onChange={handleChange}
      closeMenuOnSelect={false}
    />
  );
};
