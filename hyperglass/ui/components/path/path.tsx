import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Skeleton,
  useDisclosure,
} from '@chakra-ui/react';
import 'reactflow/dist/style.css';
import { useBreakpointValue, useColorValue, useFormState } from '~/hooks';
import { Chart } from './chart';
import { PathButton } from './path-button';

interface PathProps {
  device: string;
}

export const Path = (props: PathProps): JSX.Element => {
  const { device } = props;
  const displayTarget = useFormState(s => s.target.display);
  const getResponse = useFormState(s => s.response);
  const { isOpen, onClose, onOpen } = useDisclosure();
  const response = getResponse(device);
  const output = response?.output as AllStructuredResponses;
  const bg = useColorValue('light.50', 'dark.900');
  const centered = useBreakpointValue({ base: false, lg: true }) ?? true;
  const addResponse = useFormState(s => s.addResponse);
  return (
    <>
      <PathButton
        onOpen={async () => {
          // When opening the AS path modal, attempt on-demand ASN enrichment
          // if the response does not already contain ASN organization data.
          try {
            onOpen();
            if (!response) return;
            const out = response.output as any;
            const asnOrgs = out?.asn_organizations || {};
            if (Object.keys(asnOrgs).length > 0) return;

            // Collect unique ASNs from the output depending on type
            let asns: string[] = [];
            if (out?.routes) {
              const all = out.routes.flatMap((r: any) => r.as_path || []);
              asns = Array.from(new Set(all.map((a: any) => String(a))));
            } else if (out?.hops) {
              const all = out.hops.map((h: any) => h.asn).filter(Boolean);
              asns = Array.from(new Set(all.map((a: any) => String(a))));
            }

            if (asns.length === 0) return;

            const resp = await fetch('/api/aspath/enrich', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ as_path: asns }),
            });
            if (!resp.ok) return;
            const j = await resp.json();
            if (j?.success && j.asn_organizations) {
              // Merge ASN orgs into the stored response and update state
              out.asn_organizations = { ...(out.asn_organizations || {}), ...j.asn_organizations };
              addResponse(device, { ...response, output: out });
            }
          } catch (e) {
            // Ignore enrichment failures
            // eslint-disable-next-line no-console
            console.debug('AS path enrichment failed', e);
            onOpen();
          }
        }}
      />
      <Modal isOpen={isOpen} onClose={onClose} size="full" isCentered={centered}>
        <ModalOverlay />
        <ModalContent
          bg={bg}
          minH={{ lg: '80vh' }}
          maxH={{ base: '80%', lg: '60%' }}
          maxW={{ base: '100%', lg: '80%' }}
        >
          <ModalHeader>{`Path to ${displayTarget}`}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Skeleton isLoaded={response != null}>
              <Chart data={output} />
            </Skeleton>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};
