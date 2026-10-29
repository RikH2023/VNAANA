/*
 * Sample data for the prototype.
 * All stories, publishers, people and links are FICTIONAL.
 * Links use the reserved .example domain so they never point to a real site.
 */
import type { Story, User } from '../types'
import chipLabImage from '../assets/images/chip-lab.svg'
import heatwaveImage from '../assets/images/heatwave.svg'
import handballImage from '../assets/images/handball.svg'

export const sampleUser: User = {
  firstName: 'Kristína',
  name: 'Kristína Straková',
  username: 'kristina.s',
  initials: 'KS',
  followedTopics: ['Technology', 'Sports', 'Science'],
}

export const briefingMeta = {
  readTime: 'About 4 min',
  updatedAt: '08:10',
}

export const sampleStories: Story[] = [
  {
    id: 'eindhoven-chip-lab',
    publisher: { name: 'Brightport Tech Desk', initials: 'BT', verified: true },
    author: 'Noor Verhagen',
    publishedAgo: '2h ago',
    topic: 'Technology',
    location: 'Eindhoven',
    feedReason: 'forYou',
    whyPicked: 'You follow Tech and live near Eindhoven — this one is close to home.',
    image: {
      src: chipLabImage,
      alt: 'Illustration of a chip with circuit lines on a blue background',
    },
    title: 'Eindhoven chip lab opens its doors to student start-ups',
    summary:
      'A new shared lab in Eindhoven will let student teams test their chip designs for a fraction of the usual cost. The first 12 teams start in January.',
    why: {
      heading: 'Cheaper testing could mean more local start-ups',
      points: [
        {
          keyword: 'Cost',
          text: 'Testing a prototype chip usually costs more than a small team can raise. The lab splits that cost.',
        },
        {
          keyword: 'Jobs',
          text: 'The region already depends on chip work, and new start-ups add entry-level roles.',
        },
        {
          keyword: 'Access',
          text: 'Students, not only big companies, get time on professional equipment.',
        },
      ],
      background:
        'The Eindhoven region is one of Europe’s main chip hubs, but early-stage teams have long struggled to get lab time.',
    },
    aiNote: {
      sourceCount: 4,
      uncertainty: 'The exact price per team hasn’t been confirmed yet.',
    },
    readMore: {
      url: 'https://brightport-tech.example/eindhoven-shared-chip-lab',
      readTime: '4 min read',
      perspectives: [
        {
          publisher: 'Southern Business Wire',
          angle: 'What it means for investors in the region',
          url: 'https://southern-business-wire.example/chip-lab-investors',
        },
        {
          publisher: 'Campus Voice',
          angle: 'Students on whether 12 places is enough',
          url: 'https://campus-voice.example/chip-lab-students',
        },
      ],
    },
  },
  {
    id: 'southern-europe-heatwave',
    publisher: { name: 'Northline World Desk', initials: 'NW', verified: true },
    author: 'Elena Ruiz-Marsh',
    publishedAgo: '5h ago',
    topic: 'World',
    location: 'Southern Europe',
    feedReason: 'dontMiss',
    whyPicked:
      'You don’t follow World news, but this affects millions of people across Europe this week.',
    image: {
      src: heatwaveImage,
      alt: 'Illustration of a large sun over a hot, orange city skyline',
    },
    title: 'Heatwave pushes temperatures past 44°C across southern Europe',
    summary:
      'Spain, Italy and Greece have issued their highest heat warnings as the heatwave enters its sixth day. Cities are opening cooling centres and limiting outdoor work in the afternoon.',
    why: {
      heading: 'Heat is now a health issue, not just a weather story',
      points: [
        {
          keyword: 'Health',
          text: 'Older people and outdoor workers face the highest risk of heatstroke.',
        },
        {
          keyword: 'Travel',
          text: 'Some trains and flights are delayed as tracks and airports deal with the heat.',
        },
        {
          keyword: 'Climate',
          text: 'Scientists say heatwaves like this are becoming more frequent in Europe.',
        },
      ],
      background: 'Southern Europe has had record summer temperatures in several recent years.',
    },
    aiNote: {
      sourceCount: 6,
      uncertainty: 'Figures on heat-related deaths differ between sources and are still changing.',
    },
    readMore: {
      url: 'https://northline-world.example/southern-europe-heatwave',
      readTime: '6 min read',
      perspectives: [
        {
          publisher: 'Coastline Times',
          angle: 'How tourist towns are coping',
          url: 'https://coastline-times.example/heatwave-tourism',
        },
        {
          publisher: 'The Field Report',
          angle: 'Farmers on crop losses',
          url: 'https://field-report.example/heatwave-farms',
        },
      ],
    },
  },
  {
    id: 'rotterdam-handball-final',
    publisher: { name: 'Matchday Pulse', initials: 'MP', verified: true },
    author: 'Daan Okafor',
    publishedAgo: '9h ago',
    topic: 'Sports',
    location: 'Rotterdam',
    feedReason: 'forYou',
    whyPicked: 'You follow Sports and liked two handball stories last week.',
    image: {
      src: handballImage,
      alt: 'Illustration of a handball flying towards a goal on a green court',
    },
    title: 'Rotterdam Rivers reach their first European final in 20 years',
    summary:
      'The handball club beat a Danish side 29–27 after extra time on Saturday. The final is in three weeks, and tickets go on sale on Monday.',
    why: {
      heading: 'A small club on a big stage',
      points: [
        {
          keyword: 'Money',
          text: 'Reaching the final brings prize money that can keep the youth academy running.',
        },
        {
          keyword: 'Players',
          text: 'Several players are students who train around their classes.',
        },
        {
          keyword: 'Fans',
          text: 'Interest in handball in the city has grown since the club’s cup run began.',
        },
      ],
      background: 'The club almost folded in 2019 after losing its main sponsor.',
    },
    aiNote: {
      sourceCount: 3,
      uncertainty: 'It’s not yet confirmed which venue will host the final.',
    },
    readMore: {
      url: 'https://matchday-pulse.example/rotterdam-rivers-final',
      readTime: '3 min read',
      perspectives: [
        {
          publisher: 'Coastline Times',
          angle: 'The city’s plans for a fan zone',
          url: 'https://coastline-times.example/rivers-fan-zone',
        },
        {
          publisher: 'Sideline Weekly',
          angle: 'Tactics: how they won in extra time',
          url: 'https://sideline-weekly.example/rivers-tactics',
        },
      ],
    },
  },
]

export function findStory(id: string): Story | undefined {
  return sampleStories.find((story) => story.id === id)
}
