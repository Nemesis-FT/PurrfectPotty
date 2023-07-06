import React, {useEffect, useState} from 'react';
import Style from "./Landing.module.css";
import {Button, Heading, Chapter,} from "@steffo/bluelib-react";
import {useAppContext} from "../Context";
import {useNavigate} from "react-router-dom";
import schema from "../config";
import AdminPanel from "./Admin/AdminPanel";

export default function Dashboard() {
    const {address, setAddress} = useAppContext()
    const {token, setToken} = useAppContext()
    const navigator = useNavigate()
    const [user, setUser] = useState(null)
    const [fuse, setFuse] = useState(false)

    useEffect(() => {
        if (address === null) {
            navigator("/")
            return
        }
        if (token === null) {
            navigator("/login")
            return
        }
        getUserData();
    }, [address, token])

    async function exit() {
        setToken(null);
        navigator("/login")
    }

    async function getUserData() {
        let response = await fetch(schema + address + "/api/user/v1/me", {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + token,
            },
        });
        if (response.status === 200) {
            let values = await response.json()
            setUser(values)
        }
    }

    useEffect(() => {
        getUserData()
        const interval = setInterval(() => getUserData(), 10000)
        return () => {
            clearInterval(interval)
        }
    }, [])

    return (
        <div className={Style.Landing}>
            <div className={Style.lander} style={{minWidth: "unset"}}>
                <Heading level={1}>Dashboard</Heading>
                <Chapter>
                <p className="text-muted">
                    Salve {user ? (<>{user.username}</>) : (<>...</>)}
                </p>
                <Button children={"Logout"} onClick={e => exit()}></Button>
                </Chapter>
            </div>
            <AdminPanel/>
        </div>
    );
}