import { useState } from "react";
import "./App.scss";
import { Button } from "./components/ui/button";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <h1 className="text-3xl font-bold underline bg-red-300">Hello 🚀</h1>
      <Button>count is</Button>
    </>
  );
}

export default App;
