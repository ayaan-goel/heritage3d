// The way between the main gate and the museum: a rotating yellow arrow over a glowing circle on the ground,
// with a faint column of light above the circle. Walking into the circle takes the visitor across.
import * as THREE from "three";
import * as T from "./textures.js";

function arrowGeometry() {  // points down
  const s = new THREE.Shape();
  [[-0.17, 0.62], [0.17, 0.62], [0.17, 0.08], [0.44, 0.08], [0, -0.62], [-0.44, 0.08], [-0.17, 0.08]]
    .forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  s.closePath();
  return new THREE.ExtrudeGeometry(s, { depth: 0.14, bevelEnabled: true, bevelSize: 0.025, bevelThickness: 0.025, bevelSegments: 2 }).center();
}

export function buildPortal({ x, z, r, arrowY, arrowScale, aniso }) {
  const group = new THREE.Group();
  group.position.set(x, 0, z);

  const arrow = new THREE.Mesh(arrowGeometry(), new THREE.MeshStandardMaterial({ color: 0xffd21f, emissive: 0xc89400, roughness: 0.45 }));
  arrow.position.y = arrowY;
  arrow.scale.setScalar(arrowScale);

  const glow = { color: 0xffd21f, transparent: true, depthWrite: false, toneMapped: false, fog: false };
  const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.14, r, 64).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ ...glow, opacity: 0.95, side: THREE.DoubleSide }));
  ring.position.y = 0.03;

  const fadeUp = T.texture(T.vertical(4, 64, [[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0.28)"]]), aniso);
  fadeUp.wrapT = THREE.ClampToEdgeWrapping;
  const column = new THREE.Mesh(new THREE.CylinderGeometry(r - 0.05, r - 0.05, 1.5, 64, 1, true),
    new THREE.MeshBasicMaterial({ ...glow, map: fadeUp, side: THREE.DoubleSide }));
  column.position.y = 0.75;
  group.add(arrow, ring, column);

  return {
    group,
    animate(t) {
      arrow.rotation.y = t * 1.9;
      arrow.position.y = arrowY + Math.sin(t * 2.2) * 0.12;
      ring.scale.setScalar(1 + Math.sin(t * 3) * 0.03);
    },
  };
}
