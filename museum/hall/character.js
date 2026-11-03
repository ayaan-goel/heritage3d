// The figure seen in third-person view. For now one simple jointed stand-in, recoloured per team member;
// a real likeness of each person can replace it later without changing how it is used.
import * as THREE from "three";

export const CHARACTERS = [
  { name: "Ayaan Goel", shirt: 0x2f4d7a, trousers: 0x2b2b30, skin: 0xb98a66, hair: 0x1d1a18 },
  { name: "Kshiti Bhavsar", shirt: 0x8a3a5a, trousers: 0x33363f, skin: 0xbf8f6c, hair: 0x241c18 },
  { name: "Prof. Komal Singh", shirt: 0x3f7a6a, trousers: 0x3a3532, skin: 0xb88a68, hair: 0x201a17 },
];

const capsule = (radius, length, material) => new THREE.Mesh(new THREE.CapsuleGeometry(radius, length, 4, 12), material);

export function buildCharacter() {
  const group = new THREE.Group();
  const M = {
    shirt: new THREE.MeshStandardMaterial({ roughness: 0.85 }),
    trousers: new THREE.MeshStandardMaterial({ roughness: 0.9 }),
    skin: new THREE.MeshStandardMaterial({ roughness: 0.7 }),
    hair: new THREE.MeshStandardMaterial({ roughness: 0.8 }),
    shoe: new THREE.MeshStandardMaterial({ color: 0x1b1b1d, roughness: 0.6 }),
  };

  const torso = capsule(0.19, 0.36, M.shirt);
  torso.position.y = 1.15;
  torso.scale.z = 0.72;
  const neck = capsule(0.05, 0.06, M.skin);
  neck.position.y = 1.49;
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.115, 20, 16), M.skin);
  head.position.y = 1.63;
  head.scale.y = 1.12;
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.122, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.55), M.hair);
  hair.position.set(0, 1.655, 0.012);
  hair.scale.y = 1.05;
  group.add(torso, neck, head, hair);

  // arms and legs swing from the shoulder and the hip; their fronts face -z like the visitor's
  const limb = (x, y, radius, length, material, foot) => {
    const pivot = new THREE.Group();
    pivot.position.set(x, y, 0);
    const part = capsule(radius, length, material);
    part.position.y = -(length / 2 + radius * 0.6);
    pivot.add(part);
    if (foot) {
      const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.06, 0.24), M.shoe);
      shoe.position.set(0, -(length + radius * 1.15), -0.05);
      pivot.add(shoe);
    }
    group.add(pivot);
    return pivot;
  };
  const armL = limb(-0.245, 1.38, 0.05, 0.52, M.shirt);
  const armR = limb(0.245, 1.38, 0.05, 0.52, M.shirt);
  const legL = limb(-0.095, 0.86, 0.075, 0.68, M.trousers, true);
  const legR = limb(0.095, 0.86, 0.075, 0.68, M.trousers, true);

  // a soft dark patch on the floor, since the scenes do not draw moving shadows
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d"), grad = g.createRadialGradient(32, 32, 2, 32, 32, 32);
  grad.addColorStop(0, "rgba(0,0,0,0.45)");
  grad.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  const blob = new THREE.Mesh(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, toneMapped: false, fog: false }));
  blob.position.y = 0.035;
  group.add(blob);

  let phase = 0, swing = 0;
  return {
    group,
    wear({ shirt, trousers, skin, hair: hairColor }) {
      M.shirt.color.setHex(shirt);
      M.trousers.color.setHex(trousers);
      M.skin.color.setHex(skin);
      M.hair.color.setHex(hairColor);
    },
    pose(x, z, yaw, speed, dt) {
      group.position.set(x, 0, z);
      group.rotation.y = yaw;
      phase += speed * dt * 3.4;
      swing += (Math.min(1, speed / 2.2) * 0.62 - swing) * Math.min(1, dt * 10);
      const s = Math.sin(phase) * swing;
      legL.rotation.x = s;
      legR.rotation.x = -s;
      armL.rotation.x = -s * 0.8;
      armR.rotation.x = s * 0.8;
    },
  };
}
