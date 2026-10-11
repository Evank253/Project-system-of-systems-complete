import Marquee from "@/components/Marquee";
import Hero from "./home/Hero";
import ArchitectureMap from "./home/ArchitectureMap";
import InvariantModels from "./home/InvariantModels";
import TevvLive from "./home/TevvLive";

export default function Home() {
  return (
    <main>
      <Hero />
      <Marquee />
      <ArchitectureMap />
      <InvariantModels />
      <TevvLive />
    </main>
  );
}
