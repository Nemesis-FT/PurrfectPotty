import {useNavigate, useParams} from "react-router-dom";
import {useAppContext} from "../Context";
import {useEffect} from "react";

export default function Redirect(){
    let {addr} = useParams()
    const {address, setAddress} = useAppContext()
    const navigate = useNavigate()
    useEffect(()=>{
        console.debug("REDI",addr)
        localStorage.setItem("address", addr)
        setAddress(addr)
        navigate("/login")
    }, [addr])

    return (<div>Please wait...</div>)
}