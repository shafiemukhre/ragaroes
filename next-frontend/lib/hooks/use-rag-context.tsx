'use client'
import React, { useEffect, useState } from 'react'

export default function useRagContext() {
  const [data, setData] = useState(null)
  const [isLoading, setLoading] = useState(true)

  useEffect(() => {
    fetch('https://ragaroes-api.onrender.com/api/v1/chat/non-streaming')
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
  }, [])

  if (isLoading) return <p>Loading...</p>
  if (!data) return <p>No profile data</p>

  console.log('data -> ', data)

  return data
}
