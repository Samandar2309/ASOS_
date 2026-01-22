import { useState } from "react";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const [username, setU] = useState("");
  const [password, setP] = useState("");

  return (
    <div>
      <h2>Login</h2>
      <input placeholder="Username" onChange={e=>setU(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e=>setP(e.target.value)} />
      <button onClick={() => login(username, password)}>Kirish</button>
    </div>
  );
}
