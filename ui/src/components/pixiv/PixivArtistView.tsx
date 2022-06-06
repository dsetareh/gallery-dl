import { useEffect, useState, useRef } from 'react';
import { Space, Image, Card, Badge, Row, Col, Button, notification, Pagination, Divider } from 'antd';
import Cookies from 'universal-cookie';
import { CloudDownloadOutlined, LinkOutlined } from '@ant-design/icons';

const { Meta } = Card;
interface IPixivArtistViewProps {
    apiUrl: string
}

interface IGalleryGet {
    ID: number,
    ARTIST_ID: number,
    ARTIST_NAME: string,
    NUM_IMAGES: number,
    FILENAME: string,
    WIDTH: number,
    HEIGHT: number,
    DIRECTORYNAME: string
}

const cookies = new Cookies();

const PixivArtistView = (props: IPixivArtistViewProps) => {
    const [artistData, setArtistData] = useState<IGalleryGet[]>([])
    const [imgSize, setImgSize] = useState<number>(200)
    const [currentDownloadTasks, setCurrentDownloadTasks] = useState<string[]>([])

    const onDownloadClick = (event: any, galleryId: number) => {

        const isArchiveReady = (task_id: string) => {
            fetch(`${props.apiUrl}/api/tasks/parchive/${task_id}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data['status'] !== 'SUCCESS')
                        return
                    setCurrentDownloadTasks([])
                    notification.open({
                        key: currentDownloadTasks[0],
                        message: 'Download Ready!',
                        description: `${props.apiUrl}/${data["result"]}`,
                        duration: 5
                    });
                    window.location.href = `${props.apiUrl}/${data["result"]}`

                    clearInterval(interval)
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

        }


        let interval: number = 0;
        const submitArchiveRequest = async (artistid: number) => {
            if (typeof artistid === "undefined") {
                return null
            }
            fetch(`${props.apiUrl}/api/tasks/parchive`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'artistID': artistid
                })
            })
                .then(response => response.json())
                .then(data => {
                    setCurrentDownloadTasks([...currentDownloadTasks, data["data"]["task_id"]])
                    notification.open({
                        key: currentDownloadTasks[0],
                        message: 'Download Requested',
                        description: `DownloadID: ${data["data"]["task_id"]}`,
                        duration: 2
                    });
                    interval = setInterval(isArchiveReady, 2000, data["data"]["task_id"]);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
        submitArchiveRequest(galleryId);
    }

    const loadArtists = async () => {
        const response = await fetch(`${props.apiUrl}/api/pixiv/artists`);
        const galleries = await response.json();
        setArtistData(galleries)
    }

    useEffect(() => {

        loadArtists()

        const cookImgSize = cookies.get("imgSize")
        if (typeof cookImgSize === "string") {
            const cookImgNumSize = Number(cookImgSize)
            if (cookImgNumSize >= 100 && cookImgNumSize <= 500)
                setImgSize(cookImgNumSize)

        }

    }, []);



    const generateGalleryCard = (gallData: IGalleryGet) => {
        return (
            <Card
                style={{ width: imgSize, height: imgSize + 100 }}
                cover={
                    generateCardImage(gallData)
                }
            >

                <Button
                    onClick={e => onDownloadClick(e, gallData.ID)}
                    style={{ position: "absolute", bottom: 0, right: 0, margin: "10px" }}
                    type="primary"
                    icon={<CloudDownloadOutlined />}
                    shape="round"
                    size="small" />


                <a href={`${props.apiUrl}/grid/pixiv/artist/${gallData.ID}`}>
                    <Meta style={{ position: "relative", bottom: 0, left: 0, margin: "10px" }}
                        title={`${gallData.ARTIST_NAME} ${gallData.ARTIST_ID}`}
                        description={`${gallData.NUM_IMAGES} Image${gallData.NUM_IMAGES == 1 ? '' : 's'}`}
                    />
                </a>
            </Card>
        )
    }

    const generateCardImage = (gallData: IGalleryGet) => {
        const limiting_factor = Math.max(gallData.HEIGHT, gallData.WIDTH);
        const resize_scale = limiting_factor / imgSize;
        const resized_width = Math.floor(gallData.WIDTH / resize_scale)
        const resized_height = Math.floor(gallData.HEIGHT / resize_scale)
        const leftover_width = Math.floor((imgSize - resized_width) / 2)
        return (
            <div style={{ height: resized_height, width: resized_width, left: leftover_width, position: "relative" }}>
                <Image
                    src={`${props.apiUrl}/${gallData.DIRECTORYNAME}/${gallData.FILENAME}.webp`}
                />
            </div>


        )
    }


    return (
        <>
            <Row>
                <Col span={24}>
                    <Space size={[8, 16]} wrap>
                        {artistData.map((artdata) => generateGalleryCard(artdata))}
                        {artistData.length == 0 ? "Nothing Here...." : ""}
                    </Space>
                </Col>
            </Row>
        </>
    )


}


export default PixivArtistView;