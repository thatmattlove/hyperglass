import * as React from "react";
import { Flex } from "@chakra-ui/core";
import {BGPTable,Layout} from "app/components";

const response = {
  cached: false,
  format: "application/json",
  keywords: [],
  level: "success",
  output: {
    count: 5,
    routes: [
      {
        active: true,
        age: 1310798,
        as_path: [1299, 13335],
        communities: [
          "1299:35000",
          "14525:0",
          "14525:40",
          "14525:1021",
          "14525:2840",
          "14525:3001",
          "14525:4001",
          "14525:9003"
        ],
        local_preference: 150,
        med: 0,
        next_hop: "62.115.189.136",
        peer_rid: "2.255.254.51",
        prefix: "1.1.1.0/24",
        rpki_state: 3,
        source_as: 13335,
        source_rid: "162.158.140.1",
        weight: 170
      },
      {
        active: false,
        age: 1310792,
        as_path: [174, 13335],
        communities: [
          "174:21001",
          "174:22013",
          "14525:0",
          "14525:20",
          "14525:1021",
          "14525:2840",
          "14525:3001",
          "14525:4001",
          "14525:9001"
        ],
        local_preference: 150,
        med: 2020,
        next_hop: "100.64.0.122",
        peer_rid: "199.34.92.1",
        prefix: "1.1.1.0/24",
        rpki_state: 3,
        source_as: 13335,
        source_rid: "162.158.140.1",
        weight: 170
      },
      {
        active: false,
        age: 70883,
        as_path: [13335],
        communities: [
          "13335:10232",
          "13335:19000",
          "13335:20050",
          "13335:20500",
          "13335:20530",
          "14525:0",
          "14525:20",
          "14525:1021",
          "14525:2840",
          "14525:3002",
          "14525:4003",
          "14525:9009"
        ],
        local_preference: 250,
        med: 0,
        next_hop: "100.64.0.122",
        peer_rid: "199.34.92.5",
        prefix: "1.1.1.0/24",
        rpki_state: 3,
        source_as: 13335,
        source_rid: "172.68.129.1",
        weight: 200
      },
      {
        active: false,
        age: 70862,
        as_path: [13335],
        communities: [
          "13335:10232",
          "13335:19000",
          "13335:20050",
          "13335:20500",
          "13335:20530",
          "14525:0",
          "14525:20",
          "14525:1021",
          "14525:2840",
          "14525:3002",
          "14525:4003",
          "14525:9009"
        ],
        local_preference: 250,
        med: 0,
        next_hop: "100.64.0.122",
        peer_rid: "199.34.92.6",
        prefix: "1.1.1.0/24",
        rpki_state: 3,
        source_as: 13335,
        source_rid: "172.68.129.1",
        weight: 200
      },
      {
        active: false,
        age: 1124791,
        as_path: [174, 13335],
        communities: [
          "174:21001",
          "174:22003",
          "14525:0",
          "14525:40",
          "14525:1021",
          "14525:2840",
          "14525:3003",
          "14525:4004",
          "14525:9001"
        ],
        local_preference: 150,
        med: 25090,
        next_hop: "100.64.0.122",
        peer_rid: "199.34.92.7",
        prefix: "1.1.1.0/24",
        rpki_state: 3,
        source_as: 13335,
        source_rid: "108.162.239.1",
        weight: 200
      }
    ],
    vrf: "default",
    winning_weight: "low"
  },
  random: "60d6663342e1c1e3e1b2a6259b22023b45e0568dd7e31aeee9c453cf6e7091d5",
  runtime: 5,
  timestamp: "2020-06-06 04:38:46"
};

const Structured = () => {
  return (
    <Layout>
      <Flex my={8} maxW={["100%", "100%", "75%", "75%"]} w="100%">
        <BGPTable>{response.output}</BGPTable>
      </Flex>
    </Layout>
  );
};

export default Structured;
